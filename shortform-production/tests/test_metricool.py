import copy
import datetime as dt
import importlib.util
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import Mock, patch

spec = importlib.util.spec_from_file_location('metricool', Path(__file__).resolve().parents[1] / 'scripts/metricool.py')
m = importlib.util.module_from_spec(spec)
import sys
sys.modules[spec.name] = m
spec.loader.exec_module(m)
PROFILE = m.Profile(1, 2, 'example_creator', 'Example Brand', 'America/Los_Angeles')


def record():
    return {'id': 123, 'uuid': 'expected-uuid', 'text': 'Keep this caption', 'media': ['https://static.metricool.com/video/test.mp4'],
            'publicationDate': {'dateTime': '2099-09-10T09:00:00', 'timezone': PROFILE.timezone},
            'providers': [{'network': 'instagram', 'status': 'PENDING'}], 'draft': False, 'autoPublish': True,
            'instagramData': {'type': 'REEL'}}


class DeliveryTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)
        self.video = self.root / 'clip.mp4'
        self.video.write_bytes(b'video bytes for network mocks')
        self.post = {'video_path': str(self.video), 'caption': 'Keep this caption', 'title': 'Title', 'cta': 'caption',
                     'when': '2099-09-10T09:00:00-07:00', 'is_ai_generated': False}
        self.client = m.Client('test-token', PROFILE)
        self.client.verify_brand = Mock()

    def test_wrong_brand_stops(self):
        client = m.Client('test-token', PROFILE)
        client.api = Mock(return_value=[{'id': 1, 'userId': 2, 'instagram': 'wrong', 'label': 'Example Brand'}])
        with self.assertRaisesRegex(ValueError, 'does not match'):
            client.verify_brand()

    def test_account_override_never_reaches_network(self):
        self.client.session.request = Mock()
        with self.assertRaisesRegex(ValueError, 'override'):
            self.client.api('GET', '/admin/simpleProfiles', params={'blogId': 99})
        self.client.session.request.assert_not_called()

    def test_duplicate_caption_never_uploads(self):
        self.client.queue = Mock(return_value=[record()])
        self.client.upload = Mock()
        with self.assertRaisesRegex(ValueError, 'Matching caption'):
            self.client.schedule(self.post, self.root / 'receipt')
        self.client.upload.assert_not_called()

    def test_slot_collision_with_draft_stops(self):
        occupied = record(); occupied['text'] = 'Other post'; occupied['draft'] = True
        self.client.queue = Mock(return_value=[occupied])
        self.client.upload = Mock()
        with self.assertRaisesRegex(ValueError, 'occupied'):
            self.client.schedule(self.post, self.root / 'receipt')
        self.client.upload.assert_not_called()

    def test_uncertain_create_cannot_retry(self):
        self.client.queue = Mock(return_value=[])
        self.client.upload = Mock(return_value=record()['media'][0])
        self.client.verify_media = Mock()
        self.client.api = Mock(side_effect=RuntimeError('timeout after server accepted'))
        folder = self.root / 'receipt'
        with self.assertRaises(RuntimeError):
            self.client.schedule(self.post, folder)
        self.assertTrue((folder / 'create-intent.json').exists())
        with self.assertRaisesRegex(ValueError, 'Previous create'):
            self.client.schedule(self.post, folder)
        self.assertEqual(self.client.api.call_count, 1)

    def test_verified_rerun_does_not_create(self):
        folder = self.root / 'receipt'
        m.save(folder / 'verified.json', {'post': record(), 'sha256': m.digest(self.video)})
        self.client.get = Mock(return_value=record())
        self.client.api = Mock()
        self.client.schedule(self.post, folder)
        self.client.api.assert_not_called()

    def test_successful_create_verifies_live_post_and_hosted_bytes(self):
        live = record()
        self.client.queue = Mock(return_value=[])
        self.client.upload = Mock(return_value=live['media'][0])
        self.client.verify_media = Mock()
        self.client.api = Mock(return_value=live)
        self.client.get = Mock(return_value=live)
        folder = self.root / 'receipt'
        self.client.schedule(self.post, folder)
        saved = json.loads((folder / 'verified.json').read_text())
        self.assertEqual(saved['sha256'], m.digest(self.video))
        self.assertEqual(saved['post']['uuid'], live['uuid'])
        self.assertEqual(self.client.verify_media.call_count, 2)
        body = self.client.api.call_args.kwargs['json']
        self.assertEqual(body['providers'], [{'network': 'instagram'}])
        self.assertEqual(body['instagramData']['type'], 'REEL')

    def test_readback_caption_change_never_marks_verified(self):
        live = record()
        self.client.queue = Mock(return_value=[])
        self.client.upload = Mock(return_value=live['media'][0])
        self.client.verify_media = Mock()
        self.client.api = Mock(return_value=live)
        self.client.get = Mock(return_value=dict(live, text='unexpected'))
        folder = self.root / 'receipt'
        with self.assertRaisesRegex(ValueError, 'readback mismatch'):
            self.client.schedule(self.post, folder)
        self.assertFalse((folder / 'verified.json').exists())

    def test_move_preserves_media_caption_and_accepts_minute_rounding(self):
        before = record(); after = copy.deepcopy(before)
        after['publicationDate']['dateTime'] = '2099-09-11T09:01:00'
        self.client.get = Mock(side_effect=[before, after])
        self.client.queue = Mock(return_value=[])
        self.client.api = Mock(return_value=True)
        result = self.client.move(123, 'expected-uuid', '2099-09-11T09:01:37-07:00', self.root / 'move')
        sent = self.client.api.call_args.kwargs['json']
        self.assertEqual(set(sent), {'publicationDate'})
        self.assertEqual(result['text'], before['text'])
        self.assertEqual(result['media'], before['media'])

    def test_move_wrong_uuid_cannot_write(self):
        self.client.get = Mock(return_value=record()); self.client.api = Mock()
        with self.assertRaisesRegex(ValueError, 'identity'):
            self.client.move(123, 'wrong', 'now', self.root / 'move')
        self.client.api.assert_not_called()

    def test_move_publishing_post_cannot_write(self):
        live = record(); live['providers'][0]['status'] = 'PUBLISHING'
        self.client.get = Mock(return_value=live); self.client.api = Mock()
        with self.assertRaisesRegex(ValueError, 'pending'):
            self.client.move(123, 'expected-uuid', 'now', self.root / 'move')
        self.client.api.assert_not_called()

    def test_upload_does_not_forward_metricool_auth(self):
        tx = {'uploadType': 'MULTIPART', 'uploadId': 'test-upload', 'key': 'test-key', 'parts': [
            {'startByte': 0, 'endByte': self.video.stat().st_size, 'partNumber': 1, 'presignedUrl': 'https://example.test/upload'}]}
        self.client.api = Mock(side_effect=[tx, {'fileUrl': 'https://static.metricool.com/video/test.mp4'}])
        with patch.object(m.requests, 'put', return_value=Mock(status_code=200, headers={'ETag': 'test-etag'})) as put:
            self.client.upload(self.video, self.root / 'upload.json')
        headers = put.call_args.kwargs['headers']
        self.assertNotIn('X-Mc-Auth', headers)
        self.assertIn('x-amz-checksum-sha256', headers)
        self.assertNotIn('presignedUrl', (self.root / 'upload.json').read_text())

    def test_remote_mismatch_never_creates(self):
        self.client.queue = Mock(return_value=[])
        self.client.upload = Mock(return_value=record()['media'][0])
        self.client.verify_media = Mock(side_effect=ValueError('Hosted media bytes differ'))
        self.client.api = Mock()
        with self.assertRaisesRegex(ValueError, 'bytes differ'):
            self.client.schedule(self.post, self.root / 'receipt')
        self.client.api.assert_not_called()

    def test_duplicate_video_in_manifest_is_rejected(self):
        other = dict(self.post, when='2099-09-11T09:00:00-07:00')
        path = self.root / 'manifest.json'
        m.save(path, {'account': PROFILE.instagram, 'timezone': PROFILE.timezone, 'posts': [self.post, other]})
        with self.assertRaisesRegex(ValueError, 'Duplicate'):
            m.validate_manifest(path, PROFILE)

    def test_naive_and_past_dates_are_rejected(self):
        with self.assertRaisesRegex(ValueError, 'explicit UTC offset'):
            m.date_info('2099-09-11T09:00:00', PROFILE.timezone)
        with self.assertRaisesRegex(ValueError, 'future'):
            m.date_info('2000-09-11T09:00:00-07:00', PROFILE.timezone)

    def test_unconfigured_profile_is_rejected(self):
        with self.assertRaisesRegex(ValueError, 'positive'):
            m.Profile(None, None, 'example_creator', 'Example Brand', 'Etc/UTC')

    def test_invalid_timezone_is_rejected(self):
        with self.assertRaisesRegex(ValueError, 'IANA'):
            m.Profile(1, 2, 'example_creator', 'Example Brand', 'Invalid/Zone')

    def test_date_converts_to_configured_timezone(self):
        result = m.date_info('2099-01-10T09:00:00+00:00', 'Asia/Tokyo')
        self.assertEqual(result, {'dateTime': '2099-01-10T18:00:00', 'timezone': 'Asia/Tokyo'})

    def test_manifest_cannot_switch_accounts(self):
        path = self.root / 'manifest.json'
        m.save(path, {'account': 'other_creator', 'timezone': PROFILE.timezone, 'posts': [self.post]})
        with self.assertRaisesRegex(ValueError, 'must match'):
            m.validate_manifest(path, PROFILE)

    def test_request_failure_does_not_expose_url_or_token(self):
        self.client.session.request = Mock(side_effect=m.requests.RequestException('url?secret=do-not-expose'))
        with self.assertRaises(RuntimeError) as caught:
            self.client.api('POST', '/v2/scheduler/posts')
        self.assertNotIn('do-not-expose', str(caught.exception))


if __name__ == '__main__':
    unittest.main()

#!/usr/bin/env python3
"""Direct Metricool delivery for an explicitly configured Instagram account. Dry-run by default; credentials never logged."""
import argparse
import base64
import datetime as dt
import hashlib
import json
import os
from pathlib import Path
from urllib.parse import urlparse
from zoneinfo import ZoneInfo
from dataclasses import dataclass
try:
    import requests
except ImportError:
    raise SystemExit('Install dependencies: python3 -m pip install -r requirements.txt')

BASE = 'https://app.metricool.com/api'
@dataclass(frozen=True)
class Profile:
    blog_id: int
    user_id: int
    instagram: str
    brand_label: str
    timezone: str

    def __post_init__(self):
        if any(type(x) is not int or x <= 0 for x in (self.blog_id, self.user_id)):
            raise ValueError('Set positive blog_id and user_id values in the private profile')
        if any(not isinstance(x, str) or not x.strip() for x in (self.instagram, self.brand_label, self.timezone)):
            raise ValueError('Set instagram, brand_label, and timezone in the private profile')
        try:
            ZoneInfo(self.timezone)
        except (KeyError, ValueError):
            raise ValueError('Profile timezone must be a valid IANA timezone') from None

    @property
    def target(self):
        return {'blogId': self.blog_id, 'userId': self.user_id}



def save(path, value):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(path.suffix + '.tmp')
    tmp.write_text(json.dumps(value, indent=2, ensure_ascii=False) + '\n')
    tmp.replace(path)


def digest(path):
    h = hashlib.sha256()
    with Path(path).open('rb') as f:
        for chunk in iter(lambda: f.read(8 * 1024 * 1024), b''):
            h.update(chunk)
    return h.hexdigest()


def unpack(value):
    return value.get('data', value) if isinstance(value, dict) else value


def date_info(value, timezone, now=None):
    now = now or dt.datetime.now(ZoneInfo(timezone))
    when = now + dt.timedelta(seconds=10) if value == 'now' else dt.datetime.fromisoformat(value)
    if when.tzinfo is None:
        raise ValueError('Use an explicit UTC offset in publication times')
    if value != 'now' and when <= now:
        raise ValueError('Publication time must be in the future; use move --when now for immediate publication')
    when = when.astimezone(ZoneInfo(timezone))
    return {'dateTime': when.strftime('%Y-%m-%dT%H:%M:%S'), 'timezone': timezone}


def same_minute(a, b):
    # Metricool truncates seconds when updating publication dates.
    return a['timezone'] == b['timezone'] and a['dateTime'][:16] == b['dateTime'][:16]


class Client:
    def __init__(self, token, profile):
        if not token:
            raise ValueError('METRICOOL_API_TOKEN is required')
        self.profile = profile
        self.session = requests.Session()
        self.session.headers['X-Mc-Auth'] = token

    def api(self, method, path, **kwargs):
        params = {**self.profile.target, **kwargs.pop('params', {})}
        if any(params[k] != v for k, v in self.profile.target.items()):
            raise ValueError('Account override is not supported by this profile')
        try:
            r = self.session.request(method, BASE + path, params=params,
                                     timeout=60, allow_redirects=False, **kwargs)
        except requests.RequestException:
            raise RuntimeError('Metricool request failed; write outcome may be uncertain. Read back before retrying.') from None
        if not 200 <= r.status_code < 300:
            raise RuntimeError(f'Metricool {method} {path}: HTTP {r.status_code}; response body omitted')
        try:
            return unpack(r.json())
        except ValueError:
            raise RuntimeError('Metricool response was not JSON; read back before retrying a write') from None

    def verify_brand(self):
        brand = next((x for x in self.api('GET', '/admin/simpleProfiles') if x['id'] == self.profile.blog_id), None)
        if not brand or brand.get('userId') != self.profile.user_id or brand.get('instagram') != self.profile.instagram or brand.get('label') != self.profile.brand_label:
            raise ValueError('Metricool brand does not match the configured account')

    def get(self, post_id):
        return self.api('GET', f'/v2/scheduler/posts/{int(post_id)}')

    def queue(self, date):
        day = date['dateTime'][:10]
        return self.api('GET', '/v2/scheduler/posts', params={
            'start': day + 'T00:00:00', 'end': day + 'T23:59:59', 'timezone': self.profile.timezone})

    def upload(self, path, receipt):
        file_hash = digest(path)
        if receipt.exists():
            old = json.loads(receipt.read_text())
            if old['sha256'] != file_hash:
                raise ValueError('Cached upload does not match the file')
            return old['url']
        parts = []
        with path.open('rb') as f:
            start = 0
            for chunk in iter(lambda: f.read(8 * 1024 * 1024), b''):
                parts.append({'startByte': start, 'endByte': start + len(chunk), 'size': len(chunk),
                              'hash': base64.b64encode(hashlib.sha256(chunk).digest()).decode()})
                start += len(chunk)
        tx = self.api('PUT', '/v2/media/s3/upload-transactions', json={
            'resourceType': 'planner', 'contentType': 'video/mp4', 'fileExtension': 'mp4', 'parts': parts})
        done = []
        with path.open('rb') as f:
            if tx['uploadType'] == 'MULTIPART':
                chunks = tx['parts']
                if [(x['startByte'], x['endByte']) for x in chunks] != [(x['startByte'], x['endByte']) for x in parts]:
                    raise ValueError('Server upload ranges differ from the local file')
            elif tx['uploadType'] == 'SIMPLE' and len(parts) == 1:
                chunks = [{'startByte': 0, 'endByte': path.stat().st_size, 'presignedUrl': tx['presignedUrl']}]
            else:
                raise ValueError('Unsupported upload transaction')
            for part in chunks:
                url = part['presignedUrl']
                if urlparse(url).scheme != 'https':
                    raise ValueError('Upload URL must use HTTPS')
                f.seek(part['startByte'])
                chunk = f.read(part['endByte'] - part['startByte'])
                try:
                    # Separate request: never forward the Metricool token to storage.
                    res = requests.put(url, data=chunk, timeout=60, allow_redirects=False, headers={
                        'Content-Type': 'video/mp4',
                        'x-amz-checksum-sha256': base64.b64encode(hashlib.sha256(chunk).digest()).decode()})
                except requests.RequestException:
                    raise RuntimeError('Storage upload failed; signed URL omitted') from None
                if not 200 <= res.status_code < 300:
                    raise RuntimeError(f'Storage upload failed: HTTP {res.status_code}')
                if tx['uploadType'] == 'MULTIPART':
                    done.append({'partNumber': part['partNumber'], 'etag': res.headers['ETag']})
        body = {'multipart': {'uploadId': tx['uploadId'], 'key': tx['key'], 'parts': done}} if done else {'simple': {'fileUrl': tx['fileUrl']}}
        result = self.api('PATCH', '/v2/media/s3/upload-transactions', json=body)
        url = result.get('convertedFileUrl') or result['fileUrl']
        if digest(path) != file_hash:
            raise ValueError('Source changed during upload; do not schedule')
        save(receipt, {'sha256': file_hash, 'bytes': path.stat().st_size, 'url': url})
        return url

    def verify_media(self, url, expected):
        if urlparse(url).scheme != 'https':
            raise ValueError('Remote media must use HTTPS')
        try:
            with requests.get(url, stream=True, timeout=60) as r:
                r.raise_for_status()
                h = hashlib.sha256()
                for chunk in r.iter_content(1024 * 1024):
                    h.update(chunk)
        except requests.RequestException:
            raise RuntimeError('Remote media verification failed; URL omitted') from None
        if h.hexdigest() != expected:
            raise ValueError('Hosted media bytes differ; content verification is incomplete')

    def schedule(self, post, folder):
        self.verify_brand()
        folder.mkdir(parents=True, exist_ok=True)
        verified = folder / 'verified.json'
        if verified.exists():
            old = json.loads(verified.read_text())
            live = self.get(old['post']['id'])
            if old['sha256'] != digest(post['video_path']) or live['uuid'] != old['post']['uuid'] or live['text'] != post['caption'] or live['media'] != old['post']['media']:
                raise ValueError('Existing receipt differs from the current post; reconcile before further writes')
            return live
        if (folder / 'create-intent.json').exists():
            raise ValueError('Previous create may have succeeded. Reconcile saved request/response with the live queue; never create again blindly.')
        date = date_info(post['when'], self.profile.timezone)
        q = self.queue(date)
        if any(x.get('text') == post['caption'] for x in q):
            raise ValueError('Matching caption already exists in the queue; inspect before scheduling')
        if any(same_minute(x['publicationDate'], date) and any(p['network'] == 'instagram' for p in x['providers']) for x in q):
            raise ValueError('Instagram slot is occupied; choose a free slot')
        path = Path(post['video_path'])
        file_hash = digest(path)
        url = self.upload(path, folder / 'upload.json')
        self.verify_media(url, file_hash)
        body = {'publicationDate': date, 'text': post['caption'], 'providers': [{'network': 'instagram'}],
                'media': [url], 'autoPublish': True, 'draft': False, 'saveExternalMediaFiles': True,
                'shortener': False, 'videoCoverMilliseconds': 1000,
                'instagramData': {'autoPublish': True, 'type': 'REEL', 'showReelOnFeed': True, 'isAiGenerated': post['is_ai_generated']}}
        save(folder / 'create-intent.json', body)  # Persist before sending, including timeouts.
        created = self.api('POST', '/v2/scheduler/posts', json=body)
        save(folder / 'create-response.json', created)
        live = self.get(created['id'])
        if live['text'] != body['text'] or live['uuid'] != created['uuid'] or not same_minute(live['publicationDate'], date):
            raise ValueError('Created post readback mismatch')
        if live['draft'] or not live['autoPublish'] or live['instagramData']['type'] != 'REEL' or [p['network'] for p in live['providers']] != ['instagram'] or len(live['media']) != 1:
            raise ValueError('Created post settings mismatch')
        self.verify_media(live['media'][0], file_hash)
        save(verified, {'sha256': file_hash, 'post': live, 'verified_at': dt.datetime.now(dt.timezone.utc).isoformat()})
        return live

    def move(self, post_id, uuid, when, folder):
        self.verify_brand()
        before = self.get(post_id)
        if before['uuid'] != uuid or [x['network'] for x in before['providers']] != ['instagram']:
            raise ValueError('Post identity/network mismatch')
        if before['draft'] or not before['autoPublish'] or any(x['status'] != 'PENDING' for x in before['providers']):
            raise ValueError('Only a pending auto-published Instagram post can be moved')
        date = date_info(when, self.profile.timezone)
        if any(x['id'] != before['id'] and same_minute(x['publicationDate'], date) and any(p['network'] == 'instagram' for p in x['providers']) for x in self.queue(date)):
            raise ValueError('Instagram slot is occupied')
        folder.mkdir(parents=True, exist_ok=False)
        save(folder / 'before.json', before)
        save(folder / 'request.json', {'publicationDate': date})
        self.api('PATCH', f'/v2/scheduler/posts/{int(post_id)}', params={'fields': 'publicationDate'}, json={'publicationDate': date})
        after = self.get(post_id)
        save(folder / 'readback.json', after)
        if not same_minute(after['publicationDate'], date) or any(after[k] != before[k] for k in ('uuid', 'text', 'media')):
            raise ValueError('Move readback mismatch; inspect before retrying')
        return after


def validate_manifest(path, profile):
    data = json.loads(Path(path).read_text())
    if data.get('account') != profile.instagram or data.get('timezone') != profile.timezone:
        raise ValueError('Manifest account and timezone must match the private profile')
    posts = data.get('posts', [])
    if not posts:
        raise ValueError('Manifest has no posts')
    times, hashes = set(), set()
    for post in posts:
        video = Path(post['video_path'])
        if not video.is_absolute() or not video.is_file() or not video.stat().st_size:
            raise ValueError('Each video must be an existing nonempty absolute file path')
        if video.suffix.lower() != '.mp4':
            raise ValueError('This uploader supports MP4 files')
        if not 1 <= len(post['caption'].strip()) <= 2200 or not post.get('title', '').strip():
            raise ValueError('Each post needs a title and a caption of 1–2200 characters')
        if not post.get('cta', '').strip() or post['cta'].casefold() not in post['caption'].casefold():
            raise ValueError('Caption must contain its declared CTA; review it against the recording')
        if not isinstance(post.get('is_ai_generated'), bool):
            raise ValueError('Set is_ai_generated explicitly after inspecting the asset')
        if post['when'] == 'now':
            raise ValueError('Use an explicit future time for scheduling; move handles an existing post now')
        date = date_info(post['when'], profile.timezone)['dateTime'][:16]
        sha = digest(video)
        if date in times or sha in hashes:
            raise ValueError('Duplicate slot or video in manifest')
        times.add(date); hashes.add(sha)
    return posts


def token_from():
    token = os.environ.get('METRICOOL_API_TOKEN')
    if not token:
        raise ValueError('Set METRICOOL_API_TOKEN in the environment; do not put it in the profile')
    return token


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--profile', type=Path, required=True)
    subs = parser.add_subparsers(dest='command', required=True)
    schedule = subs.add_parser('schedule')
    schedule.add_argument('manifest', type=Path)
    schedule.add_argument('--receipts', type=Path, required=True)
    schedule.add_argument('--apply', action='store_true')
    move = subs.add_parser('move')
    move.add_argument('--id', type=int, required=True)
    move.add_argument('--uuid', required=True)
    move.add_argument('--when', required=True)
    move.add_argument('--receipts', type=Path, required=True)
    move.add_argument('--apply', action='store_true')
    inspect = subs.add_parser('inspect')
    inspect.add_argument('--id', type=int, required=True)
    args = parser.parse_args()
    profile_data = json.loads(args.profile.read_text())
    expected = {'blog_id', 'user_id', 'instagram', 'brand_label', 'timezone'}
    if set(profile_data) != expected:
        raise ValueError('Profile must contain only account IDs, account names, and timezone; never credentials')
    profile = Profile(**profile_data)
    posts = validate_manifest(args.manifest, profile) if args.command == 'schedule' else None
    if args.command != 'inspect' and not args.apply:
        print(json.dumps({'mode': 'dry-run; no network calls', 'account': profile.instagram, 'posts': posts,
                          'move': {'id': args.id, 'uuid': args.uuid, 'publicationDate': date_info(args.when, profile.timezone)} if args.command == 'move' else None}, indent=2))
        return
    client = Client(token_from(), profile)
    if args.command == 'schedule':
        for post in posts:
            live = client.schedule(post, args.receipts / digest(post['video_path']))
            print(json.dumps({'id': live['id'], 'uuid': live['uuid'], 'publicationDate': live['publicationDate'], 'providers': live['providers']}))
    else:
        if args.command == 'inspect':
            client.verify_brand()
            live = client.get(args.id)
        else:
            live = client.move(args.id, args.uuid, args.when, args.receipts)
        print(json.dumps(live, indent=2))


if __name__ == '__main__':
    try:
        main()
    except (ValueError, RuntimeError, KeyError, OSError) as error:
        raise SystemExit(str(error))

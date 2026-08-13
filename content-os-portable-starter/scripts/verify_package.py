#!/usr/bin/env python3
import hashlib, json, re, sys, zipfile
from pathlib import Path
import yaml
from jsonschema import Draft202012Validator, FormatChecker

ROOT=Path(sys.argv[1] if len(sys.argv)>1 else Path(__file__).resolve().parents[1]).resolve()
REQUIRED=["README.md","LICENSE","DATA_POLICY.md","schema/site-config.schema.json","config/site-config.template.yaml","config/site-config.example.yaml","onboarding/onboarding-questionnaire.md","connectors/connector-capability-matrix.yaml","policies/approval-policy.template.md","measurement/readback.template.yaml"]
DENY_PATH=[".git","__pycache__",".pytest_cache",".mypy_cache",".DS_Store"]
PRIVATE_PATTERNS={
 "private_abs_path":r"/(?:home|Users)/[A-Za-z0-9._-]+/",
 "session_link":r"@session:[A-Za-z0-9_-]+/",
 "pem_key":r"-----BEGIN (?:RSA |EC |OPENSSH |DSA )?PRIVATE KEY-----",
 "aws_access_key":r"AKIA[0-9A-Z]{16}",
 "github_token":r"gh[pousr]_[A-Za-z0-9]{30,}",
 "slack_token":r"xox[baprs]-[A-Za-z0-9-]{20,}",
 "generic_secret_assignment":r"(?i)(?:api[_-]?key|access[_-]?token|client[_-]?secret|password)\s*[:=]\s*[\"']?[A-Za-z0-9_./+=-]{12,}"
}
errors=[]
all_files=sorted(p for p in ROOT.rglob("*") if p.is_file())
rel=[p.relative_to(ROOT).as_posix() for p in all_files]
for req in REQUIRED:
 if req not in rel: errors.append(f"missing:{req}")
for name in rel:
 if any(part in DENY_PATH for part in Path(name).parts) or name.endswith((".pyc",".pyo")): errors.append(f"prohibited_path:{name}")
secret_hits=[]
for p,name in zip(all_files,rel):
 if p.suffix.lower() in {".zip",".png",".jpg",".jpeg",".gif",".pdf"}: continue
 text=p.read_text("utf-8")
 for label,pat in PRIVATE_PATTERNS.items():
  if re.search(pat,text): secret_hits.append({"file":name,"pattern":label})
if secret_hits: errors.append("secret_or_privacy_hits")
schema=json.loads((ROOT/"schema/site-config.schema.json").read_text())
Draft202012Validator.check_schema(schema)
validator=Draft202012Validator(schema,format_checker=FormatChecker())
yaml_results={}
for name in ["config/site-config.template.yaml","config/site-config.example.yaml"]:
 data=yaml.safe_load((ROOT/name).read_text())
 found=sorted(e.message for e in validator.iter_errors(data))
 yaml_results[name]={"valid":not found,"errors":found}
 if found: errors.append(f"schema_invalid:{name}")
for name in ["connectors/connector-capability-matrix.yaml","measurement/readback.template.yaml"]:
 try: yaml.safe_load((ROOT/name).read_text())
 except Exception as e: errors.append(f"yaml_invalid:{name}:{e}")
required_phrase="publishing is separately approved"
phrase_files=sum(required_phrase in p.read_text("utf-8").lower() for p in all_files if p.suffix.lower() in {".md",".yaml",".yml",".json"})
if phrase_files<2: errors.append("safety_phrase_missing")
result={"status":"PASS" if not errors else "FAIL","root":str(ROOT),"file_count":len(all_files),"prohibited_path_count":sum(x.startswith("prohibited_path") for x in errors),"secret_privacy_hits":secret_hits,"site_config_validation":yaml_results,"publishing_gate_phrase_files":phrase_files,"errors":errors}
print(json.dumps(result,indent=2))
sys.exit(0 if not errors else 1)

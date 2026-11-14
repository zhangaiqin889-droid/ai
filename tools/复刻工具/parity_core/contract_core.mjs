function normalizeJson(x){if(Array.isArray(x))return x.map(normalizeJson);if(x && typeof x==="object"){const out={};for(const k of Object.keys(x).sort()){if(k==="__proto__"||k==="constructor"||k==="prototype")throw Error("unsafe key");out[k]=normalizeJson(x[k]);}return out;}if(typeof x==="number"&&!Number.isFinite(x))throw Error("nonfinite");return x;}

function compareJson(a,b){return JSON.stringify(normalizeJson(a))===JSON.stringify(normalizeJson(b));}

function assertMatrix(m){if(!m||!Array.isArray(m.features))throw Error("feature matrix required");const ids=new Set();for(const f of m.features){if(!f||typeof f.id!=="string"||!f.id||ids.has(f.id))throw Error("missing/duplicate feature id");ids.add(f.id);}return ids;}

function compileContracts(m){assertMatrix(m);return {schema_version:"1.0",scope:"declared features only",cases:m.features.map(f=>({feature_id:f.id,source:f.source||"unknown",type:f.kind||"unknown",expected_behavior:f.expected_behavior||null,test_status:"NOT_VERIFIED"}))};}

function evaluateResults(m,observations){const ids=assertMatrix(m);if(!Array.isArray(observations))throw Error("observations array required");const results=new Map();for(const o of observations){if(!ids.has(o.feature_id)||results.has(o.feature_id))throw Error("unknown/duplicate feature observation");if(o.outcome!=="PASS"&&o.outcome!=="FAIL"&&o.outcome!=="BLOCKED")throw Error("invalid outcome");results.set(o.feature_id,o);}let passed=0,failed=0,blocked=0;const features=m.features.map(f=>{const o=results.get(f.id);const status=o?o.outcome:"NOT_VERIFIED";if(status==="PASS")passed++;if(status==="FAIL")failed++;if(status==="BLOCKED")blocked++;return {id:f.id,name:f.name||f.id,status,evidence:o?.evidence||null};});return {schema_version:"1.0",scope:"declared observed feature matrix",feature_count:m.features.length,passed,failed,blocked,not_verified:features.length-passed-failed-blocked,observed_scope_pass_rate:features.length?passed/features.length:null,whole_software_parity:"UNKNOWN",features};}

export { normalizeJson, compareJson, assertMatrix, compileContracts, evaluateResults };

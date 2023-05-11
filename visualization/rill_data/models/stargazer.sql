

SELECT 
_airbyte_data.starred_at, 1 as count
from read_json_auto('/tmp/airbyte_local/ods/awesome-list/_airbyte_raw_stargazers.jsonl')



/*SELECT 
_airbyte_data.*

from read_json_auto('/tmp/airbyte_local/ods/export_json/_airbyte_raw_users.jsonl') 
left outer join read_json_auto('/tmp/airbyte_local/ods/export_json/_airbyte_raw_users.jsonl')

--from read_ndjson_objects('/tmp/airbyte_local/ods/export_json/_airbyte_raw_users.jsonl')
*/


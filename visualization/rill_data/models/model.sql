select 
_airbyte_data->>'user'->>'login', 
_airbyte_data->>'repository',
*
 from _airbyte_raw_stargazers;

# Code Agent Report

## CRITICAL Issues
### .env file tracked by git (Manual)
- ./.env:0
- `File detected`
- Fix: Add to .gitignore

### .env file tracked by git (Manual)
- ./frontend/.env:0
- `File detected`
- Fix: Add to .gitignore

### .env file tracked by git (Manual)
- ./agents/chess/.env:0
- `File detected`
- Fix: Add to .gitignore

### Hardcoded razorpay_key (Manual)
- ./scripts/test-bait/bait.py:5
- `RAZORPAY_KEY = "rzp_live_abc123xyz"`
- Fix: Move to env

### Hardcoded jwt_secret (Manual)
- ./scripts/test-bait/bait.py:6
- `JWT_SECRET = "supersecretkey"`
- Fix: Move to env

### Hardcoded hardcoded_api_key (Manual)
- ./scripts/test-bait/bait.js:8
- `const API_KEY = "AIzaSyAbc123"`
- Fix: Move to env

### Hardcoded database_url (Manual)
- ```postgres://user:password@host:port/database?option=value``.`
- Fix: Move to env

### Hardcoded database_url (Manual)
- ```postgres://user:pass@host:port/database?option=value``.`
- Fix: Move to env

### Hardcoded database_url (Manual)
- ```postgres://user:pass@host:port/database?option=value``.`
- Fix: Move to env

### Hardcoded hardcoded_api_key (Manual)
- `_SK_SSH_ECDSA_NISTP256 = b"sk-ecdsa-sha2-nistp256@openssh.com"`
- Fix: Move to env

### Hardcoded hardcoded_api_key (Manual)
- `The format of a sk-ecdsa-sha2-nistp256@openssh.com public key is:`
- Fix: Move to env

### Hardcoded hardcoded_api_key (Manual)
- `string		"sk-ecdsa-sha2-nistp256@openssh.com"`
- Fix: Move to env

### Hardcoded hardcoded_api_key (Manual)
- `"sk-ecdsa-sha2-nistp256 private keys cannot be loaded"`
- Fix: Move to env

### Hardcoded hardcoded_api_key (Manual)
- `"plesk-release",`
- Fix: Move to env

### Hardcoded generic_secret (Manual)
- `url = str(self.replace(password="********"))`
- Fix: Move to env

### Hardcoded generic_secret (Manual)
- `token = "{%s}" % token.replace("}", "}}")`
- Fix: Move to env

### Hardcoded database_url (Manual)
- `e = create_engine("postgresql://scott:tiger@localhost/test")`
- Fix: Move to env

### Hardcoded database_url (Manual)
- `e = create_engine("postgresql://scott:tiger@localhost/test")`
- Fix: Move to env

### Hardcoded database_url (Manual)
- `conninfo="postgresql://scott:tiger@localhost/test",`
- Fix: Move to env

### Hardcoded database_url (Manual)
- `conninfo="postgresql://scott:tiger@localhost/test",`
- Fix: Move to env

### Hardcoded generic_secret (Manual)
- `password="tiger",`
- Fix: Move to env

### Hardcoded generic_secret (Manual)
- `password="tiger",`
- Fix: Move to env

### Hardcoded generic_secret (Manual)
- `password="tiger",`
- Fix: Move to env

### Hardcoded generic_secret (Manual)
- `password="tiger",`
- Fix: Move to env

### Hardcoded generic_secret (Manual)
- `password="tiger",`
- Fix: Move to env

### Hardcoded database_url (Manual)
- `>>> pg_engine = create_engine("postgresql://scott:tiger@localhost/test")`
- Fix: Move to env

### Hardcoded generic_secret (Manual)
- `url = url.set(password="test")`
- Fix: Move to env

### Hardcoded generic_secret (Manual)
- `default_metavalue_token = "NULL"`
- Fix: Move to env

### Hardcoded generic_secret (Manual)
- `database="db", username="user", password="passwd"`
- Fix: Move to env

### Hardcoded generic_secret (Manual)
- `password="tiger",`
- Fix: Move to env

### Hardcoded generic_secret (Manual)
- `password="tiger",`
- Fix: Move to env

### Hardcoded generic_secret (Manual)
- `password="tiger",`
- Fix: Move to env

### Hardcoded generic_secret (Manual)
- `default_metavalue_token = "DEFAULT"`
- Fix: Move to env

### Hardcoded database_url (Manual)
- `some_engine = create_engine("postgresql://scott:tiger@host/test")`
- Fix: Move to env

### Hardcoded generic_secret (Manual)
- `password = ":****"`
- Fix: Move to env

### Hardcoded hardcoded_api_key (Manual)
- `'plesk-release',`
- Fix: Move to env

### Hardcoded generic_secret (Manual)
- `username="jo@gmail.com", password="a secret"`
- Fix: Move to env

### Hardcoded database_url (Manual)
- `alembic -x dbname=postgresql://user:pass@host/dbname upgrade head`
- Fix: Move to env

### Hardcoded generic_secret (Manual)
- `upgrade_token="%s_upgrades" % name,`
- Fix: Move to env

### Hardcoded generic_secret (Manual)
- `downgrade_token="%s_downgrades" % name,`
- Fix: Move to env

### Hardcoded generic_secret (Manual)
- `user = User(username='scolvin', password='password1')`
- Fix: Move to env

### Hardcoded generic_secret (Manual)
- `model = Model(password='IAmSensitive', password_bytes=b'IAmSensitiveBytes')`
- Fix: Move to env

### Hardcoded database_url (Manual)
- `m = MyDatabaseModel(db='postgres://user:pass@localhost:5432/foobar')`
- Fix: Move to env

### Hardcoded database_url (Manual)
- `#> postgres://user:pass@localhost:5432/foobar`
- Fix: Move to env

### Hardcoded database_url (Manual)
- `MyDatabaseModel(db='postgres://user:pass@localhost:5432')`
- Fix: Move to env

### Hardcoded database_url (Manual)
- `+  where None = PostgresDsn('postgres://user:pass@localhost:5432').path [type=assertion_error, input_value='postgres://user:pass@localhost:5432', input_type=str]`
- Fix: Move to env

### Hardcoded generic_secret (Manual)
- `r += f", secret='{base64.b64encode(self.secret).decode()}'"`
- Fix: Move to env

### Hardcoded generic_secret (Manual)
- `<TotpToken token='897212' expire_time=1419622740>`
- Fix: Move to env

### Hardcoded generic_secret (Manual)
- `_dummy_secret = "too many secrets"`
- Fix: Move to env

### Hardcoded generic_secret (Manual)
- `secret = 'test'`
- Fix: Move to env

### Hardcoded generic_secret (Manual)
- `token = '781501'`
- Fix: Move to env

### Hardcoded generic_secret (Manual)
- `token = '781501'`
- Fix: Move to env

### Hardcoded generic_secret (Manual)
- `token = '781501'`
- Fix: Move to env

### Hardcoded generic_secret (Manual)
- `token = '781501'`
- Fix: Move to env

### Hardcoded generic_secret (Manual)
- `secret = "test"`
- Fix: Move to env

### Hardcoded generic_secret (Manual)
- `wrong_secret = 'stub'`
- Fix: Move to env

### Hardcoded generic_secret (Manual)
- `secret = "too many secrets" * 16`
- Fix: Move to env

### Hardcoded generic_secret (Manual)
- `password = 'stub'`
- Fix: Move to env

### Hardcoded generic_secret (Manual)
- `self.assertFalse(ctx.needs_update(hash, secret='bob'))`
- Fix: Move to env

### Hardcoded generic_secret (Manual)
- ./.pre-commit-cache/repotan8hqgf/detect_secrets/plugins/keyword.py:133
- `# e.g. my_password = "bar"`
- Fix: Move to env

### Hardcoded generic_secret (Manual)
- ./.pre-commit-cache/repotan8hqgf/detect_secrets/plugins/keyword.py:169
- `# e.g. my_password = "bar"`
- Fix: Move to env

### Hardcoded generic_secret (Manual)
- ./.pre-commit-cache/repotan8hqgf/test_data/each_secret.py:4
- `base64_secret = 'c2VjcmV0IG1lc3NhZ2Ugc28geW91J2xsIG5ldmVyIGd1ZXNzIG15IHBhc3N3b3Jk'`
- Fix: Move to env

### Hardcoded generic_secret (Manual)
- ./.pre-commit-cache/repotan8hqgf/test_data/each_secret.py:5
- `hex_secret = '8b1118b376c313ed420e5133ba91307817ed52c2'`
- Fix: Move to env

### Hardcoded generic_secret (Manual)
- ./.pre-commit-cache/repotan8hqgf/tests/filters/heuristic_filter_test.py:108
- `('secret = "hunter2"', True),`
- Fix: Move to env

### Hardcoded generic_secret (Manual)
- ./.pre-commit-cache/repotan8hqgf/tests/filters/regex_filter_test.py:22
- `assert filters.regex.should_exclude_line('password = "canarytoken"') is True`
- Fix: Move to env

### Hardcoded generic_secret (Manual)
- ./.pre-commit-cache/repotan8hqgf/tests/filters/regex_filter_test.py:23
- `assert filters.regex.should_exclude_line('password = "hunter2"') is False`
- Fix: Move to env

### Hardcoded generic_secret (Manual)
- ./.pre-commit-cache/repotan8hqgf/tests/core/potential_secret_test.py:35
- `secret = potential_secret_factory(secret='secret')`
- Fix: Move to env

### Hardcoded generic_secret (Manual)
- ./.pre-commit-cache/repotan8hqgf/tests/core/potential_secret_test.py:40
- `secret = potential_secret_factory(secret='blah')`
- Fix: Move to env

### Hardcoded generic_secret (Manual)
- ./.pre-commit-cache/repotan8hqgf/tests/core/potential_secret_test.py:66
- `secret = potential_secret_factory(type='secret_type', secret='blah')`
- Fix: Move to env

### Hardcoded generic_secret (Manual)
- ./.pre-commit-cache/repotan8hqgf/tests/core/usage/filters_usage_test.py:138
- `f.write(f'secret = "{uuid.uuid4()}"'.encode())`
- Fix: Move to env

### Hardcoded generic_secret (Manual)
- ./.pre-commit-cache/repotan8hqgf/tests/plugins/ibm_cos_hmac_test.py:93
- `('someotherpassword = "doesnt start right"', False),`
- Fix: Move to env

### Hardcoded generic_secret (Manual)
- ./.pre-commit-cache/repotan8hqgf/tests/plugins/softlayer_test.py:37
- `('softlayer_api_key= "{sl_token}"'.format(sl_token=SL_TOKEN), True),`
- Fix: Move to env

### Hardcoded generic_secret (Manual)
- ./.pre-commit-cache/repotan8hqgf/tests/plugins/softlayer_test.py:39
- `('softlayer_api_key="{sl_token}"'.format(sl_token=SL_TOKEN), True),`
- Fix: Move to env

### Hardcoded generic_secret (Manual)
- ./.pre-commit-cache/repotan8hqgf/tests/plugins/softlayer_test.py:51
- `('sl_api_key= "{sl_token}"'.format(sl_token=SL_TOKEN), True),`
- Fix: Move to env

### Hardcoded generic_secret (Manual)
- ./.pre-commit-cache/repotan8hqgf/tests/plugins/softlayer_test.py:53
- `('slapi_key="{sl_token}"'.format(sl_token=SL_TOKEN), True),`
- Fix: Move to env

### Hardcoded generic_secret (Manual)
- ./.pre-commit-cache/repotan8hqgf/tests/plugins/softlayer_test.py:68
- `('softlayer_password = "{sl_token}"'.format(sl_token=SL_TOKEN), True),`
- Fix: Move to env

### Hardcoded generic_secret (Manual)
- ./.pre-commit-cache/repotan8hqgf/tests/plugins/cloudant_test.py:59
- `('cloudant_password = "a-fake-tooshort-key"', False),`
- Fix: Move to env

### Hardcoded generic_secret (Manual)
- ./.pre-commit-cache/repotan8hqgf/tests/plugins/cloudant_test.py:60
- `('cl_api_key = "a-fake-api-key"', False),`
- Fix: Move to env

### Hardcoded hardcoded_api_key (Manual)
- ./.pre-commit-cache/repotan8hqgf/tests/plugins/github_token_test.py:11
- `('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', True),`
- Fix: Move to env

### Hardcoded hardcoded_api_key (Manual)
- ./.pre-commit-cache/repotan8hqgf/tests/plugins/stripe_key_test.py:16
- `'rk_live_5TcWfjKmJgpql9hjpRnwRXbT',`
- Fix: Move to env

### Hardcoded hardcoded_api_key (Manual)
- ./.pre-commit-cache/repotan8hqgf/tests/plugins/stripe_key_test.py:20
- `'pk_live_j5krY8XTgIcDaHDb3YrsAfCl',`
- Fix: Move to env

### Hardcoded hardcoded_api_key (Manual)
- ./.pre-commit-cache/repotan8hqgf/tests/plugins/openai_test.py:12
- `('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', True),`
- Fix: Move to env

### Hardcoded generic_secret (Manual)
- ./.pre-commit-cache/repotan8hqgf/tests/plugins/keyword_test.py:43
- `('password = "somefakekey"', None),  # 'fake' in the secret`
- Fix: Move to env

### Hardcoded generic_secret (Manual)
- ./.pre-commit-cache/repotan8hqgf/tests/plugins/keyword_test.py:108
- `('password = "somefakekey"', None),     # 'fake' in the secret`
- Fix: Move to env

### Hardcoded generic_secret (Manual)
- ./.pre-commit-cache/repotan8hqgf/tests/plugins/keyword_test.py:123
- `('password = "somefakekey"', None),     # 'fake' in the secret`
- Fix: Move to env

### Hardcoded hardcoded_api_key (Manual)
- ./.pre-commit-cache/repotan8hqgf/tests/plugins/gitlab_token_test.py:52
- `'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',`
- Fix: Move to env

### Hardcoded generic_secret (Manual)
- ./.pre-commit-cache/repotan8hqgf/tests/plugins/ibm_cloud_iam_test.py:32
- `('ibm_cloud_api_key= "{cloud_iam_key}"'.format(cloud_iam_key=CLOUD_IAM_KEY), True),`
- Fix: Move to env

### Hardcoded generic_secret (Manual)
- ./.pre-commit-cache/repotan8hqgf/tests/plugins/ibm_cloud_iam_test.py:34
- `('cloud_iam_api_key="{cloud_iam_key}"'.format(cloud_iam_key=CLOUD_IAM_KEY), True),`
- Fix: Move to env

### Hardcoded generic_secret (Manual)
- ./.pre-commit-cache/repotan8hqgf/tests/plugins/ibm_cloud_iam_test.py:47
- `('ibm_password = "{cloud_iam_key}"'.format(cloud_iam_key=CLOUD_IAM_KEY), True),`
- Fix: Move to env

### Hardcoded generic_secret (Manual)
- ./.pre-commit-cache/repotan8hqgf/tests/audit/report_test.py:21
- `first_secret = 'value1'`
- Fix: Move to env

### Hardcoded generic_secret (Manual)
- ./.pre-commit-cache/repotan8hqgf/tests/audit/report_test.py:22
- `second_secret = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxMjM0NTY3ODkwIiwibmFtZSI6IkpvaG4gRG9lIiwiaWF0IjoxNTE2MjM5MDIyfQ'  # noqa: E501`
- Fix: Move to env

### Hardcoded generic_secret (Manual)
- ./.pre-commit-cache/repotan8hqgf/tests/audit/report_test.py:24
- `aws_secret = 'AKIAZZZZZZZZZZZZZZZZ'`
- Fix: Move to env

### Hardcoded hardcoded_api_key (Manual)
- ./.pre-commit-cache/repotan8hqgf/scripts/run_performance_tests.py:211
- `'StripeDetector': 'rk_live_TESTtestTESTtestTESTtest',`
- Fix: Move to env

### Hardcoded generic_secret (Manual)
- ./.pre-commit-cache/repotan8hqgf/build/lib/detect_secrets/plugins/keyword.py:133
- `# e.g. my_password = "bar"`
- Fix: Move to env

### Hardcoded generic_secret (Manual)
- ./.pre-commit-cache/repotan8hqgf/build/lib/detect_secrets/plugins/keyword.py:169
- `# e.g. my_password = "bar"`
- Fix: Move to env

### Hardcoded generic_secret (Manual)
- ./.pre-commit-cache/repotan8hqgf/py_env-python3/lib/python3.9/site-packages/detect_secrets/plugins/keyword.py:133
- `# e.g. my_password = "bar"`
- Fix: Move to env

### Hardcoded generic_secret (Manual)
- ./.pre-commit-cache/repotan8hqgf/py_env-python3/lib/python3.9/site-packages/detect_secrets/plugins/keyword.py:169
- `# e.g. my_password = "bar"`
- Fix: Move to env

### Hardcoded generic_secret (Manual)
- ./.pre-commit-cache/repotan8hqgf/py_env-python3/lib/python3.9/site-packages/pip/_internal/utils/misc.py:472
- `password = ":****"`
- Fix: Move to env

### Hardcoded hardcoded_api_key (Manual)
- ./.pre-commit-cache/repotan8hqgf/py_env-python3/lib/python3.9/site-packages/pip/_vendor/packaging/licenses/_spdx.py:721
- `'asterisk-exception': {'id': 'Asterisk-exception', 'deprecated': False},`
- Fix: Move to env

### Hardcoded hardcoded_api_key (Manual)
- ./.pre-commit-cache/repotan8hqgf/py_env-python3/lib/python3.9/site-packages/pip/_vendor/packaging/licenses/_spdx.py:722
- `'asterisk-linking-protocols-exception': {'id': 'Asterisk-linking-protocols-exception', 'deprecated': False},`
- Fix: Move to env

### Hardcoded hardcoded_api_key (Manual)
- ./.pre-commit-cache/repotan8hqgf/py_env-python3/lib/python3.9/site-packages/pip/_vendor/distro/distro.py:153
- `"plesk-release",`
- Fix: Move to env

### Hardcoded hardcoded_api_key (Manual)
- ./.pre-commit-cache/repotan8hqgf/py_env-python3/lib/python3.9/site-packages/pip/_vendor/cachecontrol/filewrapper.py:27
- `as the temporary files directory is disk-based (sometimes it's a`
- Fix: Move to env

### Hardcoded hardcoded_api_key (Manual)
- ./.pre-commit-cache/repotan8hqgf/py_env-python3/lib/python3.9/site-packages/setuptools/_vendor/packaging/licenses/_spdx.py:721
- `'asterisk-exception': {'id': 'Asterisk-exception', 'deprecated': False},`
- Fix: Move to env

### Hardcoded hardcoded_api_key (Manual)
- ./.pre-commit-cache/repotan8hqgf/py_env-python3/lib/python3.9/site-packages/setuptools/_vendor/packaging/licenses/_spdx.py:722
- `'asterisk-linking-protocols-exception': {'id': 'Asterisk-linking-protocols-exception', 'deprecated': False},`
- Fix: Move to env

### Hardcoded hardcoded_api_key (Manual)
- ./.pre-commit-cache/repotan8hqgf/py_env-python3/lib/python3.9/site-packages/setuptools/_vendor/importlib_metadata/compat/py311.py:11
- `An example affected package is dask-labextension, which uses`
- Fix: Move to env

### Hardcoded generic_secret (Manual)
- ./.pre-commit-cache/repov03iweq2/py_env-python3/lib/python3.9/site-packages/pip/_internal/utils/misc.py:472
- `password = ":****"`
- Fix: Move to env

### Hardcoded hardcoded_api_key (Manual)
- ./.pre-commit-cache/repov03iweq2/py_env-python3/lib/python3.9/site-packages/pip/_vendor/packaging/licenses/_spdx.py:721
- `'asterisk-exception': {'id': 'Asterisk-exception', 'deprecated': False},`
- Fix: Move to env

### Hardcoded hardcoded_api_key (Manual)
- ./.pre-commit-cache/repov03iweq2/py_env-python3/lib/python3.9/site-packages/pip/_vendor/packaging/licenses/_spdx.py:722
- `'asterisk-linking-protocols-exception': {'id': 'Asterisk-linking-protocols-exception', 'deprecated': False},`
- Fix: Move to env

### Hardcoded hardcoded_api_key (Manual)
- ./.pre-commit-cache/repov03iweq2/py_env-python3/lib/python3.9/site-packages/pip/_vendor/distro/distro.py:153
- `"plesk-release",`
- Fix: Move to env

### Hardcoded hardcoded_api_key (Manual)
- ./.pre-commit-cache/repov03iweq2/py_env-python3/lib/python3.9/site-packages/pip/_vendor/cachecontrol/filewrapper.py:27
- `as the temporary files directory is disk-based (sometimes it's a`
- Fix: Move to env


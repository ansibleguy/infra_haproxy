# HAProxy Fingerprinting

We are only dealing with server-side fingerprinting.

This kind of fingerprinting only has a very limited set of information to work with - including:

* TCP data
* SSL data
* HTTP data

If you want to have a fingerprint that is unique for each client that connects, you might want to look into implementing [Client-side fingerprinting](https://wiki.superstes.eu/en/latest/1/infra/waf.html#client-side-fingerprint) in your web application frontend.

Check out my [WAF Docs](https://wiki.superstes.eu/en/latest/1/infra/waf.html) for more details.

## SSL Fingerprint (JA3N)

This fingerprint will be the same for every HTTP client. Per example: Chrome 118.1.1 will have the same one - no matter were it comes from. This can be pretty useful to track/recognize a distributed attack.

You may not want to use this kind of fingerprint for blocking clients. But it can be combined with other data to limit the block-scope.

If you enable `security.fingerprint_ssl` you can reference it using the variables:

* `var(txn.fingerprint_ssl)` => MD5 hash of JA3n fingerprint
* `var(txn.fingerprint_ssl_raw)` => raw JA3n fingerprint

To use this kind of fingerprint, you have to enable the `[SSL capture-buffer](https://www.haproxy.com/documentation/haproxy-configuration-manual/latest/#3.2-tune.ssl.capture-buffer-size)`. You may want to set it in the globals via `tune.ssl.capture-buffer-size 96`

### JA3N Notes

The basic JA3 fingerprint is currently not useful as browsers started to randomize the order of their SSL extensions.

JA3N tackles this by sorting these. See also: [tlsfingerprint.io](https://tlsfingerprint.io/norm_fp)

HAProxy Lua script that implements JA3N: [gist.github.com/superstes](https://gist.github.com/superstes/0d0a94cb70f2e2713f4a90fa88160795)

**Examples**:

* Before (JA3): `771,4865-4867-4866-49195-49199-52393-52392-49196-49200-49162-49161-49171-49172-156-157-47-53,0-23-65281-10-11-16-5-34-51-43-13-45-28-65037-41,29-23-24-25-256-257,0`
* After (JA3N): `771,4865-4867-4866-49195-49199-52393-52392-49196-49200-49162-49161-49171-49172-156-157-47-53,0-10-11-13-16-23-28-34-41-43-45-5-51-65037-65281,29-23-24-25-256-257,0`

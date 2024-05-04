# HAProxy Fingerprinting

We are only dealing with server-side fingerprinting.

This kind of fingerprinting only has a very limited set of information to work with - including:

* TCP data
* SSL data
* HTTP data

If you want to have a fingerprint that is unique for each client that connects, you might want to look into implementing [Client-side fingerprinting](https://wiki.superstes.eu/en/latest/1/infra/waf.html#client-side-fingerprint) in your web application frontend.

Check out my [WAF Docs](https://wiki.superstes.eu/en/latest/1/infra/waf.html) for more details.

## SSL Fingerprint (JA3)

This fingerprint will be the same for every HTTP client. Per example: Chrome 118.1.1 will have the same one - no matter were it comes from. This can be pretty useful to track/recognize a distributed attack.

You may not want to use this kind of fingerprint for blocking clients. But it can be combined with other data to limit the block-scope.

If you enable `security.fingerprint_ssl` you can reference it using the variables:

* `var(txn.fingerprint_ssl)` => MD5 hash of JA3 fingerprint
* `var(txn.fingerprint_ssl_raw)` => raw JA3 fingerprint

# ACA-Py External VC Holder

A quick demonstration of using an external service for holding JSON-LD creds.

The External VC Holder component is currently dependent on unmerged upstream changes to ACA-Py.

The KMS Service used by this demo can be found here: [dbluhm/mini-kms](https://github.com/dbluhm/mini-kms).


## Run the Demo

```sh
docker-compose build
docker-compose run demo
docker-compose down -v # Stop and clean up when you're done
```

You should be able to observe two requests to the `kms` service by running:

```sh
docker-compose logs kms
```

There should be one request to the key generation endpoint and one to the signing endpoint.

Logs from the ACA-Py instance may also be of interest:

```sh
docker-compose logs holder
```


## Points of Interest

See the [package init](/acapy_vc_holder/__init__.py) for an example of instantiating and loading the External Provider in ACA-Py.

See [provider.py](/acapy_vc_holder/provider.py) to see the implementation of the External Provider itself.

# AWS Shadows HTTP API

Using the HTTP API of AWS is a mess. To make it easier, AWS develops two solutions : the SDK and the CLI.

However, in IoT, we don't want to download GB of codes on our things. The more codes are downloads, the more it consumes battery.

I wanted to manipulte a part of AWS IoT Core : AWS Shadows. But only with natives modules of python.

## Requirements

- Python 3.10 >=

## How does it works ?

With this repo you can :

- GET a shadow of a thing

In the TODO list of this repo, there are :

- UPDATE a shadow
- DELETE a shadow

### GET a Shadow

- Shadow Method = GET
- HTTP Method = GET
- Host = data-ats.iot.*region*.amazonaws.com
- URI = /things/*thing_name*/shadow
- Queries = shadow_name=*shadow_name*

### UPDATE a Shadow

- Shadow Method = UPDATE
- HTTP Method = POST
- Host = data-ats.iot.*region*.amazonaws.com
- URI = /things/*thing_name*/shadow
- Queries = shadow_name=*shadow_name*

### DELETE a Shadow

- Shadow Method = DELETE
- HTTP Method = DELETE
- Host = data-ats.iot.*region*.amazonaws.com
- URI = /things/*thing_name*/shadow
- Queries = shadow_name=*shadow_name*

## How to manipulate AWS HTTP API ?

AWS Documentation :

- Shadows : <https://docs.aws.amazon.com/iot/latest/developerguide/device-shadow-rest-api.html>
- Create a Request : <https://docs.aws.amazon.com/general/latest/gr/signing-aws-api-requests.html>

Those documentations are pretty good but not complete, so here is how I do to create a request to use its API. You can find out that it's the same as AWS but more precise sometimes, and specifically for the shadows.

### Step 1 - Create a canonical request

Create a string like this (with the newlines) :

``` text
HTTPMethod 
CanonicalUri
CanonicalQueryString
CanonicalHeaders
SignedHeaders
HashedPayload
```

Where :

- ```HTTPMethod``` --> HTTP method (GET, POST,...)
- ```CanonicalUri``` --> The part of the url between the host and the queries (those after "?")
- ```CanonicalQueryString``` --> The queries (those after "?") ; Empty string if none
- ```CanonicalHeaders``` --> Headers in alphabetic order ; ```host``` if HTTP/1.1 and ```:authority``` if HTTP/2 ; others keys start with ```x-amz-*```
- ```SignedHeaders``` --> Keys 'list from section ```CanonicalHeaders``` finishing with an empty newline
- ```HashedPayload``` --> Body's payload of HTTP request hashed with the hasing algorithm ```SHA256```

### Step 2 - Hash the canonical request

Using the same algorithm as ```HashedPayload``` from the canonical request, hash the entire string of the canonical request.

### Step 3 - Create a string to sign

Create a string, that will be use for the signature, like this (with the newlines) :

``` text
Algorithm
RequestDateTime
CredentialScope
HashedCanonicalRequest
```

- ```Algorithm``` --> The algorithm used to create the hash of the canonical request. For ```SHA256```, the algorithm is ```AWS4-HMAC-SHA256```
- ```RequestDateTime``` --> The date and time in the following format : *YYYYMMDD*T*hhmmss*Z (T and Z are statics letters, not numbers)
- ```CredentialScope``` --> The string has the following format : ```YYYYMMDD/region/service/aws4_request```.
- ```HashedCanonicalRequest``` --> The hash calculated in the previous section

### Step 4 - Calculate the signature

The signature is calculate in 5 steps. Each step is a part of the ```CredentialScope``` from previous section. They use the hmac-sha256 algorithm :

1. ```kDate = hmac-sha256("AWS4" + Key, Date)``` --> Key is your ```AWS Secret Acess Key``` and Date from ```CredentialScope```
2. ```kRegion = hmac-sha256(kDate, Region)``` -->  Region from ```CredentialScope```
3. ```kService = hmac-sha256(kRegion, Service)``` --> Service from ```CredentialScope```
4. ```kSigning = hmac-sha256(kService, "aws4_request")```
5. ```signature = hmac-sha256(kSigning, string-to-sign)``` --> string-to-sign is the all string from previous step

### Step 5 - Set up the new request

Add the ```Authorization``` header like this (without the newlines, here they are just use to read easier the value) :

``` text
Authorization: "AWS4-HMAC-SHA256 
Credential=<aws access key id>/<CredentialScope>,
SignedHeaders=<SignedHeaders>,
Signature=<signature>"
```

Where :

- ```CredentialScope``` is the same as step 3
- ```SignedHeaders``` is the same as step 1
- ```signature``` si the same as step 4

## Example

### My canonical request

``` text
GET
/things/amder-toto/shadow

host:data-ats.iot.eu-west-1.amazonaws.com
x-amz-date:20230109T092953Z

host;x-amz-date
e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855
```

- ```HTTPMethod``` -  GET method
- ```CanonicalUri``` - /things/amder-toto/shadow and "amder-toto" is the name of my thing
- ```CanonicalQueryString``` - empty string because none
- ```CanonicalHeaders``` - host + x-amz-date + newline
- ```SignedHeaders``` - host;x-amz-date
- ```HashedPayload``` - e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855 is the hash of an empty payload

### My canonical request's hash

I hashed the entire string from step 1 with ```SHA256``` algorithm.

``` text
bf90448c05591761ce8f87bcd848604e6ccd81a7b7b8d4df0dd02b4db7b158d7
```

### My string to sign

``` text
AWS4-HMAC-SHA256
20230109T092953Z
20230109/eu-west-1/iotdata/aws4_request
bf90448c05591761ce8f87bcd848604e6ccd81a7b7b8d4df0dd02b4db7b158d7
```

- ```Algorithm``` - AWS4-HMAC-SHA256
- ```CredentialScope``` - 20230109T092953Z (remind format : YYYYMMDDThhmmssZ ; T and Z are statics letters, not numbers)
- ```HashedCanonicalRequest``` - 20230109/eu-west-1/iotdata/aws4_request because date/region/service/aws4_request
- ```RequestDateTime``` - bf90448c05591761ce8f87bcd848604e6ccd81a7b7b8d4df0dd02b4db7b158d7 is from step 2

### My signature

By following the 5 step to calculate the signature, I get

``` text
kDate = hmac-sha256("AWS42iZtXXXXXXXXXXX/XXXXXX", 20230109)

kRegion = hmac-sha256(kDate, eu-west-1) 

kService = hmac-sha256(kRegion, iotdata) 

kSigning = hmac-sha256(kService, "aws4_request") 

signature = hmac-sha256(kSigning, "AWS4-HMAC-SHA256
20230109T092953Z
20230109/eu-west-1/iotdata/aws4_request
bf90448c05591761ce8f87bcd848604e6ccd81a7b7b8d4df0dd02b4db7b158d7")
```

My result (To protect my data, this hash is fake, but in a correct format) :

``` text
3c6b9506c7fa621d1b51ae669b7b56576904f0c0e6bcd5d4e91f1ccedcb03a42
```

### My new request

I construct this new header :

``` text
{'Authorization': 'AWS4-HMAC-SHA256 Credential=AKIAEXAMPLE/20230109/eu-west-1/iotdata/aws4_request SignedHeaders=host;x-amz-date Signature=3c6b9506c7fa621d1b51ae669b7b56576904f0c0e6bcd5d4e91f1ccedcb03a42'}
```

And my request is :

- HTTP method = GET
- URL = <https://data-ats.iot.eu-west-1.amazonaws.com/things/amder-toto/shadow>
- Headers = {
    'Authorization': 'AWS4-HMAC-SHA256 Credential=AKIAEXAMPLE/20230109/eu-west-1/iotdata/aws4_request SignedHeaders=host;x-amz-date Signature=3c6b9506c7fa621d1b51ae669b7b56576904f0c0e6bcd5d4e91f1ccedcb03a42',
    'X-Amz-Date': '20230109T092953Z'
}

# ICGW MQTT Setup Support Tool

This is a script for ICGW (IoT Connect Gateway) MQTT Protocol Conversion which currently support the following actions:

- Batch update SIMs with adding `azureDeviceId` and `gcpDeviceId` to current SIM records.
- Add devices to Azure IoT and GCP IoT services.
- Add authentications to ICGW.

## Setup

### Prepare Azure and GCP Authentication Information

#### Azure

For Azure, you only need to provide the proper `connectionString` in the yaml file.

How to identify the `connectionString`:

1. Login to Azure Portal.
2. Go to `IoT Hub` and select the hub you want to create/update.
3. Click `Shared access policies` under `Security settings`, then choose the shared access policies that with permission `Registry Write`. You can properly use `iothubowner` created by default.
4. Click the policy selected in step 3, then click the copy icon under `Primary connection string`. This is the `connectionString`.

#### GCP

Normally, you will need a service account (in JSON format) with permission that can create or update the IoT devices.

Once you create the service account, download the JSON key file and set the path of it with environment variable `GOOGLE_APPLICATION_CREDENTIALS` in your computer. The script will directly search for it.
You can also provide the path directly by setting `serviceAccount` in the GCP yaml file. You can refer to the Yaml file section for details.

### Environment variables

You need to setup the SDP authentication details with environment variables. Please create a `.env` file with the following content:

```env
SDP_API_HOST=<SDP HOST>
SDP_API_TENANT_ID=<YOUR SDP TENANT ID>
SDP_API_KEY=<YOUR API KEY>
SDP_API_SECRET=<YOUR API SECRET>
```

### Install Python packages

Install necessary python packages by the following commands:

```bash
pip install requirements.txt
```

## Tools

### Batch Update SIMs

This will update multiple SIMs with the Azure Device ID and GCP Device ID through SDP API.

Run the following command to batch update SIMs by yaml files.

```bash
python main.py update-sims <PATH OF YAML FILES>
```

You can set the value to empty string and the tools will set the value to be `null` in this case.

### Add Devices to Cloud

This will add devices to specific cloud service. If same device ID is found in the cloud service, the setting will be updated and overwritten with the YAML one.

Run the following command to add Devices by yaml files.

```bash
python main.py add-devices <PATH OF YAML FILES>
```

### Add Authentications

This will add one or more authentications through SDP API. Their authentications will be always created as new one with yaml files.

Run the following command to add Authentications by yaml files.

```bash
python main.py add-authentications <PATH OF YAML FILES>
```

### Yaml files

The format of yaml should follow the format below.

If same options are specified both in `top` and `devices` level, the `devices` will be used.

#### GCP

```yaml
gcpSettings:
  serviceAccount: <SERVICE ACCOUNT JSON FILE>
  projectId: <PROJECT-ID>
  region: <REGION>
  registryId: <REGISTRY-ID>
  options: // Default options
    - name: format
      value: RSA_PEM
    - name: public_key
      value: certs/gcp_public.pem
  devices:
    - imsi: <IMSI 1>
      deviceId: <DEVICE ID 1 (GCP DEVICE ID)>
    - imsi: <IMSI 2>
      deviceId: <DEVICE ID 2 (GCP DEVICE ID)>
      options: // Device Specific Options
        - name: format
          value: ES256_X509_PEM
        - name: public_key
          value: certs/gcp_public.pem
  authentications:
    - name: <NAME>
      algorithm: <ALGORITHM>
      privateKey: <PRIVATE KEY FILE>
      deviceId: <DEVICE ID>
      description: <DESCRIPTION>
```

- `service_account` is optional. Script will search for environment variable `GOOGLE_APPLICATION_CREDENTIALS` for service account json file if this is not specified.
- `projectId`, `region`, `registryId` and `devices` are **required**.
- Multiple credentials is not supported. Devices will only create or update with exactly 1 credential.
- For `options`:
  - `format` can be `RSA_PEM`, `RSA_X509_PEM`, `ES256_PEM`, `ES256_X509_PEM` or nothing (Empty String or not set).
  - If `format` is nothing (Empty String or not set), no credentials for the device.
  - If `format` is set, `public_key` is **required** and the value should be the path of the key.
- For `authentications`:
  - `name`, `algorithm`, `privateKey`, `deviceId` are **required**.
  - `algorithm` can be `RS256` or `ES256`.
  - `privateKey` can be file path.
  - `deviceId` is arbitrary value. This `deviceId` does not have to match deviceId under the devices option.
  - `description` is optional.

#### Azure

```yaml
azureSettings:
  connectionString: <AZURE CONNECTION STRING>
  options: // Default options
    - name: type
      value: SAS
    - name: primary_key
      value: old-value
    - name: secondary_key
      value: old-value
    - name: primary_thumbprint
      value: old-value
    - name: secondary_thumbprint
      value: old-value
    - name: status
      value: disabled
  devices:
    - imsi: <IMSI 1>
      deviceId: <DEVICE ID 1 (AZURE DEVICE ID)>
      options: // Device Specific Options
        - name: primary_key
          value: new-value
        - name: secondary_key
          value: new-value
        - name: status
          value: enabled
    - imsi: <IMSI 2>
      deviceId: <DEVICE ID 2 (AZURE DEVICE ID)>
      options: 
        - name: type
          value: X509
        - name: primary_thumbprint
          value: new-value
        - name: secondary_thumbprint
          value: new-value
  authentications:
    - name: <NAME>
      sharedAccessKey: <SHARED ACCESS KEY>
      deviceId: <DEVICE ID>
      description: "HOGE"
```

- `connectionString` and `devices` are **required**.
- For `options`:
  - `type` is **required** for all devices. It should be either `SAS` (SAS authentication), `X509` (X509 authentication) or `CA` (certificate authority).
  - `primary_key` and `secondary_key` are required if `type` is `SAS`.
  - `primary_thumbprint` and `secondary_thumbprint` are required if `type` is `X509`.
  - `status` is optional, can be either `enabled` or `disabled`. If no valid value is specified, `enabled` will be set.
- For `authentications`:
  - `name`, `sharedAccessKey`, `deviceId` are **required**.
  - `deviceId` is arbitrary value. This `deviceId` does not have to match deviceId under the devices option.
  - `description` is optional.

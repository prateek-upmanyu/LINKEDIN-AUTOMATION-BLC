import sodium from 'libsodium-wrappers';

export async function encryptSecret(secret: string, publicKey: string) {
  await sodium.ready;
  const binkey = sodium.from_base64(publicKey, sodium.base64_variants.ORIGINAL);
  const binsec = sodium.from_string(secret);
  const encBytes = sodium.crypto_box_seal(binsec, binkey);
  return sodium.to_base64(encBytes, sodium.base64_variants.ORIGINAL);
}

export async function getRepoPublicKey(owner: string, repo: string, token: string) {
  const res = await fetch(https://api.github.com/repos///actions/secrets/public-key, {
    headers: {
      Authorization: 	oken ,
      Accept: 'application/vnd.github.v3+json',
      'X-GitHub-Api-Version': '2022-11-28',
    },
  });

  if (!res.ok) {
    throw new Error(Failed to fetch public key: );
  }

  return res.json();
}

export async function putRepoSecret(
  owner: string,
  repo: string,
  secretName: string,
  encryptedValue: string,
  keyId: string,
  token: string
) {
  const res = await fetch(https://api.github.com/repos///actions/secrets/, {
    method: 'PUT',
    headers: {
      Authorization: 	oken ,
      Accept: 'application/vnd.github.v3+json',
      'X-GitHub-Api-Version': '2022-11-28',
    },
    body: JSON.stringify({
      encrypted_value: encryptedValue,
      key_id: keyId,
    }),
  });

  if (!res.ok && res.status !== 201 && res.status !== 204) {
    throw new Error(Failed to set secret : );
  }
}

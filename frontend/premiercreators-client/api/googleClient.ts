import axios from "axios";

export function initGoogleClient(token: string) {
  const config = {
    method: "get",
    url: "http://209.97.134.126:81/api/client/google/init_google_client",
    headers: {
      Authorization: `Bearer ${token}`,
    },
  };
  return axios(config);
}

export function uploadServiceAccountCredentials(token: string, data: FormData) {
  const config = {
    method: "post",
    url: "http://209.97.134.126:81/api/client/google/upload_credentials",
    data: data,
    headers: {
      Authorization: `Bearer ${token}`,
      "Content-Type": "multipart/form-data",
    },
  };
  return axios(config);
}

export function checkGoogleClientState(token: string) {
  const config = {
    method: "get",
    url: "http://209.97.134.126:81/api/client/google/google_client_state",
    headers: {
      Authorization: `Bearer ${token}`,
    },
  };

  return axios(config);
}


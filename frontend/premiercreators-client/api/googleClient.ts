import axios from "axios";

export function initGoogleClient(token: string) {
  const config = {
    method: "get",
    url: "https://5000-williammoko-221212james-219vby8q3s9.ws-eu86.gitpod.io/api/client/google/init_google_client",
    headers: {
      Authorization: `Bearer ${token}`,
    },
  };
  return axios(config);
}

export function uploadServiceAccountCredentials(token: string, data: FormData) {
  const config = {
    method: "post",
    url: "https://5000-williammoko-221212james-219vby8q3s9.ws-eu86.gitpod.io/api/client/google/upload_credentials",
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
    url: "https://5000-williammoko-221212james-219vby8q3s9.ws-eu86.gitpod.io/api/client/google/google_client_state",
    headers: {
      Authorization: `Bearer ${token}`,
    },
  };

  return axios(config);
}


import axios from "axios";

export function setImgurCredentials(token: string, data: any) {
  const config = {
    method: "post",
    url: "http://209.97.134.126/api/client/imgur/set_imgur_credentials",
    headers: {
      Authorization: `Bearer ${token}`,
      "Content-Type": "application/json",
    },
    data: data,
  };

  return axios(config);
}

export function setImgurClientRefreshToken(token: string, data: any) {
  const config = {
    method: "post",
    url: "http://209.97.134.126/api/client/imgur/set_imgur_refresh_token",
    headers: {
      Authorization: `Bearer ${token}`,
      "Content-Type": "application/json",
    },
    data: data,
  };

  return axios(config);
}

export function checkImgurClientState(token: string, cid: string) {
  const config = {
    method: "get",
    url: `http://209.97.134.126/api/client/imgur/imgur_client_state/${cid}`,
    headers: {
      Authorization: `Bearer ${token}`,
    },
  };

  return axios(config);
}

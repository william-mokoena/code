import axios from "axios";

export function setRedditCredentials(token: string, data: any) {
  const config = {
    method: "post",
    url: "http://209.97.134.126:81/api/client/reddit/set_reddit_credentials",
    headers: {
      Authorization: `Bearer ${token}`,
      "Content-Type": "application/json",
    },
    data: data,
  };

  return axios(config);
}

export function setRedditClientRefreshToken(token: string, data: any) {
  const config = {
    method: "post",
    url: "http://209.97.134.126:81/api/client/reddit/set_reddit_refresh_token",
    headers: {
      Authorization: `Bearer ${token}`,
      "Content-Type": "application/json",
    },
    data: data,
  };

  return axios(config);
}

export function checkRedditClientState(token: string, cid: string) {
  const config = {
    method: "get",
    url: `http://209.97.134.126:81/api/client/reddit/reddit_client_state/${cid}`,
    headers: {
      Authorization: `Bearer ${token}`,
    },
  };

  return axios(config);
}

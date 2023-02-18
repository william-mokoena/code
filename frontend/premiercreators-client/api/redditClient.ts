import axios from "axios";

export function setRedditCredentials(token: string, data: any) {
  const config = {
    method: "post",
    url: "https://5000-williammoko-221212james-219vby8q3s9.ws-eu86.gitpod.io/api/client/reddit/set_reddit_credentials",
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
    url: "https://5000-williammoko-221212james-219vby8q3s9.ws-eu86.gitpod.io/api/client/reddit/set_reddit_refresh_token",
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
    url: `https://5000-williammoko-221212james-219vby8q3s9.ws-eu86.gitpod.io/api/client/reddit/reddit_client_state/${cid}`,
    headers: {
      Authorization: `Bearer ${token}`,
    },
  };

  return axios(config);
}

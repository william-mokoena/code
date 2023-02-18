import axios from "axios";

export function setCloutsyCredentials(token: string, data: any) {
  const config = {
    method: "post",
    url: "https://5000-williammoko-221212james-219vby8q3s9.ws-eu86.gitpod.io/api/client/cloutsy/set_cloutsy_credentials",
    headers: {
      Authorization: `Bearer ${token}`,
      "Content-Type": "application/json",
    },
    data: data,
  };

  return axios(config);
}

export function checkCloutsyClientState(token: string) {
  const config = {
    method: "get",
    url: `https://5000-williammoko-221212james-219vby8q3s9.ws-eu86.gitpod.io/api/client/cloutsy/cloutsy_client_state`,
    headers: {
      Authorization: `Bearer ${token}`,
    },
  };

  return axios(config);
}

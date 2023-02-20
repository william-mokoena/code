import axios from "axios";

export function setCloutsyCredentials(token: string, data: any) {
  const config = {
    method: "post",
    url: "http://209.97.134.126:81/api/client/cloutsy/set_cloutsy_credentials",
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
    url: `http://209.97.134.126:81/api/client/cloutsy/cloutsy_client_state`,
    headers: {
      Authorization: `Bearer ${token}`,
    },
  };

  return axios(config);
}

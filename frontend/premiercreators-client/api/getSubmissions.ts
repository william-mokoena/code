import axios from "axios";

export default function addSubreddit(token: string) {
  const config = {
    method: "get",
    url: `http://209.97.134.126:81/api/submissions`,
    headers: {
      Authorization: `Bearer ${token}`,
    },
  };

  return axios(config);
}

import axios from "axios";

export default function addSubreddit(token: string) {
  const config = {
    method: "get",
    url: `https://5000-williammoko-221212james-219vby8q3s9.ws-eu86.gitpod.io/api/submissions`,
    headers: {
      Authorization: `Bearer ${token}`,
    },
  };

  return axios(config);
}

import axios from "axios";

export default function getSubreddits(token: string) {
  const config = {
    method: "get",
    maxBodyLength: Infinity,
    url: "https://5000-williammoko-221212james-219vby8q3s9.ws-eu86.gitpod.io/api/subreddits",
    headers: {
      Authorization: `Bearer ${token}`,
    },
  };
  return axios(config);
}

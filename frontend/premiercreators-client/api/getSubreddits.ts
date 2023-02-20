import axios from "axios";

export default function getSubreddits(token: string) {
  const config = {
    method: "get",
    maxBodyLength: Infinity,
    url: "http://209.97.134.126/api/subreddits",
    headers: {
      Authorization: `Bearer ${token}`,
    },
  };
  return axios(config);
}

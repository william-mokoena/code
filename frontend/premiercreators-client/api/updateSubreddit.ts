import axios from "axios";

export default function addSubreddit(token: string, data: any) {
  const config = {
    method: "patch",
    url: "https://5000-williammoko-221212james-219vby8q3s9.ws-eu86.gitpod.io/api/update_subreddit",
    headers: {
      Authorization: `Bearer ${token}`,

      "Content-Type": "application/json",
    },
    data: data,
  };

  return axios(config);
}

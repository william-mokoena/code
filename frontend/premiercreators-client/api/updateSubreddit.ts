import axios from "axios";

export default function addSubreddit(token: string, data: any) {
  const config = {
    method: "patch",
    url: "http://209.97.134.126:81/api/update_subreddit",
    headers: {
      Authorization: `Bearer ${token}`,

      "Content-Type": "application/json",
    },
    data: data,
  };

  return axios(config);
}

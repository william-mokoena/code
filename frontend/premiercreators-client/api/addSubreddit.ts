import axios from "axios";

export default function addSubreddit(
  token: string,
  subredditName: any,
  verificationRequired: boolean
) {
  const config = {
    method: "get",
    url: `https://5000-williammoko-221212james-219vby8q3s9.ws-eu86.gitpod.io/api/add_subreddit?name=${subredditName}&verificationRequired=${verificationRequired}`,
    headers: {
      Authorization: `Bearer ${token}`,
    },
  };

  return axios(config);
}

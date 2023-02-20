import axios from "axios";

export default function addSubreddit(
  token: string,
  subredditName: any,
  verificationRequired: boolean
) {
  const config = {
    method: "get",
    url: `http://209.97.134.126/api/add_subreddit?name=${subredditName}&verificationRequired=${verificationRequired}`,
    headers: {
      Authorization: `Bearer ${token}`,
    },
  };

  return axios(config);
}

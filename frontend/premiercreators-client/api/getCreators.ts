import axios from "axios";

export default function getCreators(
  token: string,
  data: { sheetId: string; dataRange: string }
) {
  const config = {
    method: "post",
    url: "https://5000-williammoko-221212james-219vby8q3s9.ws-eu86.gitpod.io/api/get_creators",
    data: JSON.stringify(data),
    headers: {
      Authorization: `Bearer ${token}`,
      "Content-Type": "application/json",
    },
  };
  return axios(config);
}

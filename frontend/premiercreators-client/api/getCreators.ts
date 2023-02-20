import axios from "axios";

export default function getCreators(
  token: string,
  data: { sheetId: string; dataRange: string }
) {
  const config = {
    method: "post",
    url: "http://209.97.134.126/api/get_creators",
    data: JSON.stringify(data),
    headers: {
      Authorization: `Bearer ${token}`,
      "Content-Type": "application/json",
    },
  };
  return axios(config);
}

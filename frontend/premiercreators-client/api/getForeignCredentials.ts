import axios from "axios";

export default function getForeignCredentials(token: string, cid: string) {
  const config = {
    method: "get",
    url: `http://209.97.134.126:81/api/foreign_get_credentials/${cid}`,
    headers: {
      Authorization: `Bearer ${token}`,
    },
  };

  return axios(config);
}

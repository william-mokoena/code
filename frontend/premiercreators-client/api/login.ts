import axios from "axios";

export default function login(username: string, userPassword: string) {
  const data = JSON.stringify({
    name: username,
    password: userPassword,
  });

  const config = {
    method: "post",
    url: "http://209.97.134.126:81/login",
    headers: {
      "Content-Type": "application/json",
    },
    data: data,
  };

  return axios(config);
}

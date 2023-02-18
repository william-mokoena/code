import axios from "axios";

export default function login(username: string, userPassword: string) {
  const data = JSON.stringify({
    name: username,
    password: userPassword,
  });

  const config = {
    method: "post",
    url: "https://5000-williammoko-221212james-219vby8q3s9.ws-eu86.gitpod.io/login",
    headers: {
      "Content-Type": "application/json",
    },
    data: data,
  };

  return axios(config);
}

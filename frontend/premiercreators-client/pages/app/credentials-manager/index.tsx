import { useEffect, useState } from "react";
import { useRouter } from "next/router";

import { getCookieAsObject } from "../../../utils/utils";
import Credentials from "./components/Credentials";
import AppShellLayout from "../layout";

export default function CredentialsManagerPage() {
  const router = useRouter();
  const [token, setToken] = useState<string | undefined>(undefined);

  useEffect(() => {
    const _token = getCookieAsObject().token;
    setToken(_token);
    if (_token === "" || !_token) router.push("/login");
  },[setToken,router]);
  return (
    <AppShellLayout>
      {token ? <Credentials token={token} /> : <></>}
    </AppShellLayout>
  );
}

import { useEffect, useState } from "react";
import { useRouter } from "next/router";

import SubmissionsTable from "./components/SubmissionsTable";
import { getCookieAsObject } from "../../../utils/utils";
import AppShellLayout from "../layout";

import getSubreddits from "../../../api/getSubreddits";
import getSubmissions from "../../../api/getSubmissions";

export default function CredentialsManagerPage() {
  const router = useRouter();
  const [token, setToken] = useState<string | undefined>(undefined);

  const [submissions, setSubmissions] = useState();
  const [subreddits, setSubreddits] = useState();

  useEffect(() => {
    const _token = getCookieAsObject().token;
    setToken(_token);
    if (_token === "" || !_token) router.push("/login");

    if (!submissions) {
      getSubmissions(_token)
        .then((response) => {
          setSubmissions(response.data.data);
        })
        .catch((err) => console.log("something broke"));
    }

    if (!subreddits) {
      getSubreddits(_token)
        .then((response) => {
          setSubreddits(response.data.data);
        })
        .catch((err) => console.log("something broke"));
    }
  }, [setToken, router]);

  return (
    <AppShellLayout>
      {subreddits ? (
        submissions ? (
          <>
            <SubmissionsTable
              submissions={submissions}
              subreddits={subreddits}
            />
          </>
        ) : (
          <>Loading</>
        )
      ) : (
        <>Loading</>
      )}
    </AppShellLayout>
  );
}

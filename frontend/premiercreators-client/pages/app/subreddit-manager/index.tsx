import { useEffect, useState } from "react";
import { useRouter } from "next/router";

import { useInputState } from "@mantine/hooks";
import {
  ActionIcon,
  Button,
  Checkbox,
  Divider,
  Flex,
  Table,
  TextInput,
} from "@mantine/core";

import { IconRefresh } from "@tabler/icons";

import { getCookieAsObject } from "../../../utils/utils";
import AppShellLayout from "../layout";

import getSubreddits from "../../../api/getSubreddits";
import addSubreddit from "../../../api/addSubreddit";

export default function CredentialsManagerPage() {
  const router = useRouter();
  const [token, setToken] = useState<string | undefined>(undefined);

  useEffect(() => {
    const _token = getCookieAsObject().token;
    setToken(_token);
    if (_token === "" || !_token) router.push("/login");
  }, [setToken, router]);

  return (
    <AppShellLayout>
      {token ? (
        <>
          <AddSubreddit token={token} />
          <Divider />
          <br />
          <SelectSubreddits token={token} />
        </>
      ) : (
        <></>
      )}
    </AppShellLayout>
  );
}

const AddSubreddit = ({ token }: { token: string }) => {
  const [stringValue, setStringValue] = useInputState("");
  const [verificationRequired, setVerificationRequired] = useInputState(false);

  return (
    <>
      <h2>Add Subreddit</h2>
      <Flex
        mih={50}
        mt="md"
        gap="md"
        justify="flex-start"
        align="flex-start"
        direction="row"
        wrap="wrap"
        style={{ width: "50vw" }}
      >
        <TextInput
          value={stringValue}
          onChange={setStringValue}
          placeholder={"Enter a subreddit"}
        />
        <Button
          onClick={() => addSubreddit(token, stringValue, verificationRequired)}
        >
          Add
        </Button>
        <Checkbox
          onChange={(e) => setVerificationRequired(e.currentTarget.checked)}
          label={"Verification is required"}
        />
      </Flex>
    </>
  );
};

const SelectSubreddits = ({ token }: { token: string }) => {
  const [subreddits, setSubreddits] = useState<undefined | []>();

  useEffect(() => {
    getSubreddits(token).then((response) => {
      console.log(response)
      setSubreddits(response.data.data);
    });
  }, []);

  const RenderSubredditRows = () => {
    return subreddits?.map((subreddit, index) => (
      <tr key={index}>
        <td>{subreddit["name"]}</td>
        <td>{JSON.stringify(subreddit["verification_required"])}</td>
      </tr>
    ));
  };

  return (
    <>
      <Flex
        gap="md"
        justify="flex-start"
        align="center"
        direction="row"
        wrap="wrap"
        style={{ width: "100%" }}
      >
        <h2>Active Subreddits</h2>
        <ActionIcon>
          <IconRefresh
            onClick={() => {
              getSubreddits(token).then((response) => {
                setSubreddits(response.data.data);
              });
            }}
          />
        </ActionIcon>
      </Flex>
      <Table>
        <thead>
          <tr>
            <th>Subreddit</th>
            <th>Verification Required</th>
          </tr>
        </thead>
        <tbody>{subreddits ? RenderSubredditRows() : <></>}</tbody>
      </Table>
    </>
  );
};

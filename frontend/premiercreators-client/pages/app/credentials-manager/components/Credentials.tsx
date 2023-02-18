import { useEffect, useState, Fragment } from "react";
import {
  Accordion,
  Divider,
  Flex,
  Select,
  FileInput,
  TextInput,
  Group,
  Button,
  Badge,
} from "@mantine/core";
import { useForm } from "@mantine/form";
import { showNotification } from "@mantine/notifications";

import {
  uploadServiceAccountCredentials,
  initGoogleClient,
  checkGoogleClientState,
} from "../../../../api/googleClient";

import {
  setRedditCredentials,
  setRedditClientRefreshToken,
  checkRedditClientState,
} from "../../../../api/redditClient";
import {
  setImgurCredentials,
  setImgurClientRefreshToken,
  checkImgurClientState,
} from "../../../../api/imgurClient";
import getCreators from "../../../../api/getCreators";
import getForeignCredentials from "../../../../api/getForeignCredentials";
import {
  checkCloutsyClientState,
  setCloutsyCredentials,
} from "../../../../api/cloutsyClient";

export default function Credentials({ token }: { token: string }) {
  const [creator, setCreator] = useState();
  const [googleActive, setGoogleActive] = useState(false);

  return (
    <>
      <CloutsyClientForm token={token} />
      <br />
      <br />
      <Divider my="sm" />
      <GoogleClientForm token={token} setGoogleActive={setGoogleActive} />
      <br />
      <br />
      <Divider my="sm" />
      {googleActive ? (
        <SelectCreator token={token} setCreator={setCreator} />
      ) : null}
      {creator ? (
        <>
          <br />
          <Divider my="sm" />
          <h3>{"Creator's Clients"}</h3>
          <Accordion variant="separated">
            <Accordion.Item value="reddit-client">
              <Accordion.Control>Reddit Client</Accordion.Control>
              <Accordion.Panel>
                <RedditClientForm token={token} creatorObj={creator} />
              </Accordion.Panel>
            </Accordion.Item>
            <Accordion.Item value="imgur-client">
              <Accordion.Control>Imgur Client</Accordion.Control>
              <Accordion.Panel>
                <ImgurClientForm token={token} creatorObj={creator} />
              </Accordion.Panel>
            </Accordion.Item>
          </Accordion>
        </>
      ) : null}
    </>
  );
}

const CloutsyClientForm = ({ token }: { token: string }) => {
  const [clientActiveState, setClientActiveState] = useState(false);

  const form = useForm({
    initialValues: {
      apiKey: "",
    },
  });

  useEffect(() => {
    checkCloutsyClientState(token).then((response) => {
      if (response.data.data.state === "active") setClientActiveState(true);
    });
  }, []);
  return (
    <>
      <h2>Cloutsy Client</h2>
      {clientActiveState ? (
        <Badge size="lg" radius="xl" color="teal">
          ACTIVE
        </Badge>
      ) : (
        <>
          <TextInput
            required
            label="API Key"
            placeholder="Cloutsy API Key"
            {...form.getInputProps("apiKey")}
          />

          <Group position="left" mt="xl">
            <Button
              disabled={form.values.apiKey === ""}
              variant="filled"
              onClick={() => {
                if (form.values.apiKey !== "")
                  setCloutsyCredentials(
                    token,
                    JSON.stringify({ ...form.values })
                  ).then((response) => {
                    if (response.data.status === "SUCCESSFUL") {
                      setClientActiveState(true);
                      return showNotification({
                        title: "Success",
                        message: "Credentials uploaded",
                        color: "green",
                      });
                    } else if (response.data.status === "UNSUCCESSFUL") {
                      return showNotification({
                        title: "Error",
                        message: "Something went wrong please try again",
                        color: "red",
                      });
                    }
                  });
              }}
            >
              SEND
            </Button>
          </Group>
        </>
      )}
    </>
  );
};

const GoogleClientForm = ({
  token,
  setGoogleActive,
}: {
  token: string;
  setGoogleActive: Function;
}) => {
  const [file, setFile] = useState<File | null>(null);
  const [uploaded, setUploaded] = useState<boolean>(false);

  useEffect(() => {
    checkGoogleClientState(token).then((response) => {
      if (response.data.data.state === "active") setUploaded(true);
    });
  }, []);
  return (
    <>
      <h2>Google Client</h2>
      <Flex
        mih={50}
        mt="md"
        gap="md"
        justify="flex-start"
        align="flex-start"
        direction="column"
        wrap="wrap"
        style={{ width: "50vw" }}
      >
        <FileInput
          placeholder="Upload credentials"
          label="Service Account Credentials"
          description="upload service account credentials"
          variant="filled"
          disabled={uploaded}
          onChange={(file) => {
            if (file) setFile(file);
          }}
          style={{ width: "100%" }}
        />
        {uploaded ? (
          <Button
            variant="filled"
            onClick={() => {
              initGoogleClient(token).then((response) => {
                if (response.data.status === "SUCCESSFUL")
                  setGoogleActive(true);
              });
            }}
          >
            ACTIVATE
          </Button>
        ) : (
          <Button
            variant="filled"
            disabled={!file}
            onClick={() => {
              if (file) {
                const formData = new FormData();
                formData.append("file", file);
                uploadServiceAccountCredentials(token, formData).then(
                  (response) => {
                    if (response.data.status === "SUCCESSFUL")
                      setUploaded(true);
                  }
                );
              }
            }}
          >
            SEND
          </Button>
        )}
      </Flex>
    </>
  );
};

const SelectCreator = ({
  token,
  setCreator,
}: {
  token: string;
  setCreator: Function;
}) => {
  const [dataReceived, setDataReceived] = useState({ status: "", data: "" });
  const [creators, setCreators] = useState<Array<{
    cid: string;
    full_name: string;
  }> | null>();

  const form = useForm({
    initialValues: {
      sheetId: "",
      dataRange: "",
    },
  });

  return (
    <>
      <h2>Creator</h2>
      <h3>Google Sheets Client Configuration</h3>
      <Flex
        mih={50}
        mt="md"
        gap="md"
        justify="flex-start"
        align="flex-end"
        direction="row"
        wrap="wrap"
      >
        <TextInput
          required
          label="Creators Sheet ID"
          placeholder="xxxxxxx"
          {...form.getInputProps("sheetId")}
        />
        <TextInput
          required
          label="Worksheet Name and Data Range"
          placeholder="_sheet!A1:B10"
          {...form.getInputProps("dataRange")}
        />

        <Button
          variant="outline"
          onClick={() => {
            getCreators(token, form.values).then((response) => {
              if (response.data.status === "SUCCESSFUL") {
                setCreators(response.data.data);
              } else if (response.data.status === "UNSUCCESSFUL") {
                return showNotification({
                  title: "Error",
                  message: "Something went wrong please try again",
                  color: "red",
                });
              }
            });
          }}
        >
          SEND
        </Button>
      </Flex>

      {creators ? (
        <>
          <br />
          <Divider my="sm" />
          <h3>Available Creators</h3>
          <Select
            searchable
            label="Available creators"
            placeholder="Select a creator"
            data={creators.map((creator, index) => ({
              value: creator?.cid,
              label: creator?.full_name,
            }))}
            onChange={(value) => {
              const creator = creators.filter((_creator) => {
                if (_creator.cid === value) return _creator;
              })[0];

              getForeignCredentials(token, creator.cid).then((response) => {
                if (response.data.status === "SUCCESSFUL")
                  setCreator({ ...creator, credentials: response.data.data });
              });
            }}
          />
        </>
      ) : null}
    </>
  );
};

const RedditClientForm = ({
  token,
  creatorObj,
}: {
  token: string;
  creatorObj: any;
}) => {
  const [oauthURL, setOauthURL] = useState();
  const [clientActiveState, setClientActiveState] = useState(false);
  const [proxies, setProxies] = useState({});

  const form = useForm({
    initialValues: {
      username: "",
      clientId: "",
      clientSecret: "",
      userAgent: "",
      redirectUri: "",
    },
  });

  useEffect(() => {
    const credentials = creatorObj.credentials.reddit;
    form.setFieldValue("username", credentials.username);
    form.setFieldValue("clientId", credentials.client_id);
    form.setFieldValue("clientSecret", credentials.client_secret);

    checkRedditClientState(token, creatorObj.cid).then((response) => {
      if (response.data.data.state === "active") setClientActiveState(true);
    });
  }, []);

  return (
    <>
      {clientActiveState ? (
        <Badge size="lg" radius="xl" color="teal">
          ACTIVE
        </Badge>
      ) : (
        <Fragment>
          <TextInput
            required
            label="Client ID"
            placeholder="Creators reddit client id"
            {...form.getInputProps("clientId")}
          />
          <TextInput
            required
            mt="md"
            label="Client Secret"
            placeholder="Creators reddit client secret"
            {...form.getInputProps("clientSecret")}
          />
          <TextInput
            required
            mt="md"
            label="Username"
            placeholder="Creators reddit username"
            {...form.getInputProps("username")}
          />
          <TextInput
            required
            mt="md"
            label="User Agent"
            placeholder="Creators reddit user agent"
            {...form.getInputProps("userAgent")}
          />
          <TextInput
            required
            mt="md"
            label="Redirect URI"
            placeholder="Creators reddit redirect uri"
            {...form.getInputProps("redirectUri")}
          />
          <TextInput
            required
            mt="md"
            label="HTTP Proxy"
            placeholder="HTTP Proxy"
            onChange={(e) => {
              e.preventDefault();
              setProxies((prevState) => {
                return {
                  ...prevState,
                  http: e.target.value,
                };
              });
            }}
          />

          <TextInput
            required
            mt="md"
            label="HTTPS Proxy"
            placeholder="HTTPS proxy"
            onChange={(e) => {
              e.preventDefault();
              setProxies((prevState) => {
                return {
                  ...prevState,
                  https: e.target.value,
                };
              });
            }}
          />
          <Flex
            mih={50}
            mt="md"
            gap="md"
            justify="flex-start"
            align="flex-end"
            direction="row"
            wrap="wrap"
          >
            <TextInput
              required
              readOnly={!oauthURL}
              sx={{ width: "70%" }}
              label="Authorization Code"
              placeholder="Not yet created"
              {...form.getInputProps("authorizationCode")}
            />
            {oauthURL ? (
              <Button
                variant="filled"
                onClick={() => {
                  window.open(oauthURL);
                }}
              >
                AUTHENTICATE
              </Button>
            ) : (
              <Button
                ml="sm"
                mt="xl"
                variant="outline"
                onClick={() => {
                  setRedditCredentials(
                    token,
                    JSON.stringify({ ...form.values, proxies: proxies })
                  ).then((response) => {
                    if (response.data.status === "SUCCESSFUL")
                      setOauthURL(response.data.data.url);
                  });
                }}
              >
                GENERATE
              </Button>
            )}
          </Flex>

          <Group position="center" mt="xl">
            <Button
              disabled={!oauthURL}
              variant="filled"
              onClick={() =>
                setRedditClientRefreshToken(
                  token,
                  JSON.stringify({
                    ...form.values,
                    _cid: creatorObj.cid,
                    proxies: proxies,
                  })
                ).then((response) => {
                  if (response.data.status === "SUCCESSFUL") {
                    return showNotification({
                      title: "Success",
                      message: "Credentials uploaded",
                      color: "green",
                    });
                  } else if (response.data.status === "UNSUCCESSFUL") {
                    return showNotification({
                      title: "Error",
                      message: "Something went wrong please try again",
                      color: "red",
                    });
                  }
                })
              }
            >
              SEND
            </Button>
          </Group>
        </Fragment>
      )}
    </>
  );
};

const ImgurClientForm = ({
  token,
  creatorObj,
}: {
  token: string;
  creatorObj: any;
}) => {
  const [oauthURL, setOauthURL] = useState();
  const [clientActiveState, setClientActiveState] = useState(false);

  const form = useForm({
    initialValues: {
      clientId: "",
      clientSecret: "",
      accountUsername: "",
    },
  });

  useEffect(() => {
    console.log(creatorObj);
    const credentials = creatorObj.credentials.imgur;
    form.setFieldValue("accountUsername", credentials.username);
    form.setFieldValue("clientId", credentials.client_id);
    form.setFieldValue("clientSecret", credentials.client_secret);

    checkImgurClientState(token, creatorObj.cid).then((response) => {
      if (response.data.data.state === "active") setClientActiveState(true);
    });
  }, []);
  return (
    <>
      {clientActiveState ? (
        <Badge size="lg" radius="xl" color="teal">
          ACTIVE
        </Badge>
      ) : (
        <Fragment>
          <TextInput
            required
            label="Client ID"
            placeholder="Creators imgur client id"
            {...form.getInputProps("clientId")}
          />
          <TextInput
            required
            mt="md"
            label="Client Secret"
            placeholder="Creators imgur client secret"
            {...form.getInputProps("clientSecret")}
          />
          <TextInput
            required
            mt="md"
            label="Account Username"
            placeholder="Creators imgur account username"
            {...form.getInputProps("accountUsername")}
          />
          <TextInput
            required
            mt="md"
            readOnly={!oauthURL}
            label="Access Token"
            placeholder="Not yet created"
            {...form.getInputProps("accessToken")}
          />
          <TextInput
            required
            mt="md"
            readOnly={!oauthURL}
            label="Expires In"
            placeholder="Not yet created"
            {...form.getInputProps("expiresIn")}
          />
          <Flex
            mih={50}
            mt="md"
            gap="md"
            justify="flex-start"
            align="flex-end"
            direction="row"
            wrap="wrap"
          >
            <TextInput
              required
              readOnly={!oauthURL}
              sx={{ width: "70%" }}
              label="Refresh Token"
              placeholder="Not yet created"
              {...form.getInputProps("refreshToken")}
            />
            {oauthURL ? (
              <Button
                variant="filled"
                onClick={() => {
                  window.open(oauthURL);
                }}
              >
                AUTHENTICATE
              </Button>
            ) : (
              <Button
                ml="sm"
                mt="xl"
                variant="outline"
                onClick={() => {
                  setImgurCredentials(token, JSON.stringify(form.values)).then(
                    (response) => {
                      if (response.data.status === "SUCCESSFUL")
                        setOauthURL(response.data.data.url);
                    }
                  );
                }}
              >
                GENERATE
              </Button>
            )}
          </Flex>

          <Group position="center" mt="xl">
            <Button
              disabled={!oauthURL}
              variant="filled"
              onClick={() =>
                setImgurClientRefreshToken(
                  token,
                  JSON.stringify({ ...form.values, _cid: creatorObj.cid })
                ).then((response) => {
                  if (response.data.status === "SUCCESSFUL") {
                    return showNotification({
                      title: "Success",
                      message: "Credentials uploaded",
                      color: "green",
                    });
                  } else if (response.data.status === "UNSUCCESSFUL") {
                    return showNotification({
                      title: "Error",
                      message: "Something went wrong please try again",
                      color: "red",
                    });
                  }
                })
              }
            >
              SEND
            </Button>
          </Group>
        </Fragment>
      )}
    </>
  );
};

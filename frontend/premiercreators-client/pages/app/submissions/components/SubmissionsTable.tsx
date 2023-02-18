import { useState, useEffect } from "react";

import {
  Badge,
  Box,
  Button,
  Divider,
  Group,
  MultiSelect,
  Stack,
  Text,
} from "@mantine/core";
import { DataTable } from "mantine-datatable";

import { getCookieAsObject } from "../../../../utils/utils";

import updateSubmission from "../../../../api/updateSubmission";
import updateSubreddit from "../../../../api/updateSubreddit";

/*
map posts to subreddits
submission [post | post | post] --> {subreddit}

- Display each post and its text data fields
- Add delete and approve action buttons
- Search, filter and sort

*/

const PAGE_SIZE = 10;

export default function SubmissionsTable({
  submissions,
  subreddits,
}: {
  submissions: [];
  subreddits: [Subreddit];
}) {
  const [page, setPage] = useState(1);
  const [records, setRecords] = useState(submissions?.slice(0, PAGE_SIZE));

  useEffect(() => {
    const from = (page - 1) * PAGE_SIZE;
    const to = from + PAGE_SIZE;
    setRecords(submissions?.slice(from, to));
  }, [page]);

  return (
    <>
      <Box sx={{ height: "70%" }}>
        <DataTable
          withColumnBorders
          columns={[
            { accessor: "_id", noWrap: true },
            { accessor: "cid", noWrap: true },
            { accessor: "title" },
          ]}
          records={records}
          totalRecords={records?.length}
          recordsPerPage={PAGE_SIZE}
          page={page}
          onPageChange={(p) => setPage(p)}
          idAccessor={"_id"}
          rowExpansion={{
            content: ({ record }) => (
              <SubmissionContent record={record} subreddits={subreddits} />
            ),
          }}
        />
      </Box>
    </>
  );
}

const SubmissionContent = ({
  record,
  subreddits,
}: {
  record: any;
  subreddits: [Subreddit];
}) => {
  const [searchValue, onSearchChange] = useState("");
  const [selectedFlair, setSelectedFlair] = useState("");
  const { token } = getCookieAsObject();

  return (
    <>
      <Box p={24}>
        <Text fw={700} fz="md">
          {"Metadata"}
        </Text>
        <br />
        <Text fw={700}>{"Subreddit"}</Text>
        <Text>{`name: ${record["subreddit_name"]}`}</Text>
      </Box>
      <Box p={24}>
        <Stack>
          <Group>
            <Text fw={700} fz="md">
              {record["title"]}
            </Text>
            <Badge color="pink" variant="outline">
              NSFW
            </Badge>
          </Group>
          <>{record["img_link"]}</>
          {subreddits.map((subreddit, index) => {
            if (
              subreddit.name === record["subreddit_name"] &&
              subreddit.flairs.length > 0
            )
              return (
                <>
                  <MultiSelect
                    data={subreddit.flairs.map((flair) => ({
                      value: JSON.stringify({
                        subredditId: subreddit._id,
                        flair: flair,
                      }),
                      label: flair.text,
                    }))}
                    maxSelectedValues={1}
                    label="Select flair"
                    placeholder="Pick all that you like"
                    searchable
                    searchValue={searchValue}
                    onSearchChange={onSearchChange}
                    onChange={(value) => setSelectedFlair(value[0])}
                    nothingFound="Nothing found"
                  />
                  {subreddit.defaultFlair ? (
                    <>
                      <Text fw={700}>{"Default flair is: "}</Text>
                      <Badge sx={{ minWidth: "75px", maxWidth: "150px" }} variant={"outline"} color={"blue"} size={"md"}>
                        {subreddit.defaultFlair.text}
                      </Badge>
                    </>
                  ) : (
                    ""
                  )}
                </>
              );
          })}
          <br />
          <Divider />
          <Group>
            <Button
              uppercase
              disabled={record["approved"]}
              variant="filled"
              color={"green"}
              onClick={() => {
                // Check if a new flair has been chosen as the default
                if (selectedFlair !== "") {
                  // If flair has been selected set approved field to true and flair_id field to the new flair id
                  // execute both updateSubmission and updateSubreddit
                  const {
                    subredditId,
                    flair,
                  }: { subredditId: string; flair: Flair } =
                    JSON.parse(selectedFlair);

                  updateSubmission(token, {
                    _id: record["_id"],
                    fields: {
                      approved: true,
                      flair_id: flair.id,
                    },
                  });

                  updateSubreddit(token, {
                    _id: subredditId,
                    fields: {
                      defaultFlair: flair,
                    },
                  });
                } else {
                  // If no flair has been selected set approved field to true and execute updateSubmission
                  updateSubmission(token, {
                    _id: record["_id"],
                    fields: {
                      approved: true,
                    },
                  });
                }
              }}
            >
              approve
            </Button>
          </Group>
        </Stack>
      </Box>
    </>
  );
};

type Flair = {
  allowable_content: string;
  background_color: string;
  css_class: string;
  id: string;
  max_emojis: number;
  mod_only: false;
  richtext: [];
  text: string;
  text_color: string;
  text_editable: false;
  type: string;
};

type Subreddit = {
  _id: string;
  defaultFlair: Flair;
  flairs: [Flair];
  name: string;
  post_requirements: {
    body_blacklisted_strings: [];
    body_regexes: [];
    body_required_strings: [];
    body_restriction_policy: string | null;
    body_text_max_length: null;
    body_text_min_length: null;
    domain_blacklist: [];
    domain_whitelist: [];
    gallery_captions_requirement: string | null;
    gallery_max_items: number | null;
    gallery_min_items: number | null;
    gallery_urls_requirement: string | null;
    guidelines_display_policy: null;
    guidelines_text: string | null;
    is_flair_required: false;
    link_repost_age: string | null;
    link_restriction_policy: string | null;
    title_blacklisted_strings: [];
    title_regexes: [];
    title_required_strings: [];
    title_text_max_length: string | null;
    title_text_min_length: string | null;
  };
  type: "subreddit";
  verification_required: false;
};

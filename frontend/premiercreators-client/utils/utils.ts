export const getCookieAsObject = () => {
  if (document) {
    if (document.cookie === "") return {};
    else {
      const cookies = document.cookie
        .split(";")
        .map((v) => v.split("="))
        .reduce((acc: any, v) => {
          acc[decodeURIComponent(v[0].trim())] = decodeURIComponent(
            v[1].trim()
          );
          return acc;
        }, {});

      return cookies;
    }
  }
};

export const removeCookie = (cookieName: string) => {
  if (document) {
    // This function will attempt to remove a cookie from all paths.
    let pathBits = window.location.pathname.split("/");
    let pathCurrent = " path=";

    // do a simple pathless delete first.
    document.cookie = cookieName + "=; expires=Thu, 01-Jan-1970 00:00:01 GMT;";

    for (let i = 0; i < pathBits.length; i++) {
      pathCurrent +=
        (pathCurrent.substring(-1) != "/" ? "/" : "") + pathBits[i];
      document.cookie =
        cookieName +
        "=; expires=Thu, 01-Jan-1970 00:00:01 GMT;" +
        pathCurrent +
        ";";
    }
  }
};

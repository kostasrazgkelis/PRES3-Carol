import axios from "axios";

// export const getFilesA = async () =>
//   await axios.get("http://localhost:9500/show-files?directory=pretransformed_data", null, {});
//
// export const getFilesB = async () =>
//   await axios.get("http://snf-33343.ok-kno.grnetcloud.net:9500/show-files?directory=pretransformed_data", null, {});
//
// export const joinFiles = async (postRes) =>
//   await axios.post("http://snf-33344.ok-kno.grnetcloud.net:9000/start", postRes);

export const getFilesA = async () =>
  await axios.get(process.env.REACT_APP_URI_HOST_SHOW_FILES_A, null, {});

export const getFilesB = async () =>
  await axios.get(process.env.REACT_APP_URI_HOST_SHOW_FILES_A, null, {});

export const joinFiles = async (postRes) =>
  await axios.post(process.env.REACT_APP_JOIN_FILES_A_B, postRes);

import axios from "axios";

export const getFilesA = async () =>
  await axios.get(process.env.REACT_APP_URI_HOST_SHOW_FILES_A, null, {});

export const getFilesB = async () =>
  await axios.get(process.env.REACT_APP_URI_HOST_SHOW_FILES_B, null, {});

export const joinFiles = async (postRes) =>
  await axios.post(process.env.REACT_APP_JOIN_FILES_A_B, postRes);

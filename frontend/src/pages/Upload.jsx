// Upload.jsx → VIDEO INPUT PAGE

import { useState } from "react";
import { useNavigate } from "react-router-dom";
import Layout from "../components/Layout";
import UploadBox from "../components/UploadBox";
import StatusBanner from "../components/StatusBanner";
import { uploadVideo } from "../api/trafficApi";

const SUPPORTED_EXTENSIONS = [".mp4", ".mov", ".avi", ".mkv", ".webm"];

function validateFile(file) {
  if (!file) {
    return "Please select a video file before uploading.";
  }

  if (file.size <= 0) {
    return "The selected file is empty.";
  }

  const extension = file.name.toLowerCase().slice(file.name.lastIndexOf("."));
  const isVideoMime = file.type.startsWith("video/");
  const isSupportedExtension = SUPPORTED_EXTENSIONS.includes(extension);

  if (!isVideoMime && !isSupportedExtension) {
    return "Please choose a supported video format: MP4, MOV, AVI, MKV, or WebM.";
  }

  return null;
}

function Upload() {
  const [videos, setVideos] = useState({});
  const [uploading, setUploading] = useState(false);
  const [status, setStatus] = useState(null);
  const navigate = useNavigate();

  const handleDrop = (e, road) => {
    e.preventDefault();
    const file = e.dataTransfer.files[0];
    const validationError = validateFile(file);

    if (validationError) {
      setStatus({ type: "error", title: "Unsupported file", message: validationError });
      return;
    }

    setVideos((prev) => ({ ...prev, [road]: file }));
    setStatus({
      type: "info",
      title: "Video ready",
      message: `${file.name} has been added to ${road.toUpperCase()}.`,
    });
  };

  const handleChange = (e, road) => {
    const file = e.target.files[0];
    const validationError = validateFile(file);

    if (validationError) {
      setStatus({ type: "error", title: "Unsupported file", message: validationError });
      e.target.value = "";
      return;
    }

    setVideos((prev) => ({ ...prev, [road]: file }));
    setStatus({
      type: "info",
      title: "Video ready",
      message: `${file.name} has been added to ${road.toUpperCase()}.`,
    });
  };

  const handleUpload = async () => {
    const selectedVideos = Object.entries(videos).filter(([, file]) => file);

    if (selectedVideos.length === 0) {
      setStatus({ type: "error", title: "No video selected", message: "Please add at least one video before processing." });
      return;
    }

    const invalidSelection = selectedVideos.find(([, file]) => validateFile(file));
    if (invalidSelection) {
      setStatus({ type: "error", title: "Invalid selection", message: "One or more selected files are not supported. Please review the uploads and try again." });
      return;
    }

    try {
      setUploading(true);
      setStatus({
        type: "info",
        title: "Uploading videos",
        message: "Your files are being processed. This may take a moment.",
      });

      const formData = new FormData();
      selectedVideos.forEach(([road, file]) => formData.append(road, file));

      const data = await uploadVideo(formData);
      console.log("Upload successful:", data);
      setVideos({});
      setStatus({
        type: "success",
        title: "Upload successful",
        message: "The traffic videos were processed successfully. You can review the live dashboard now.",
      });
    } catch (error) {
      console.error("Upload error:", error);
      setStatus({
        type: "error",
        title: "Upload failed",
        message: error.message || "The upload could not be completed. Please try again.",
      });
    } finally {
      setUploading(false);
    }
  };

  return (
    <Layout>
      <div className="max-w-5xl mx-auto px-6 py-16 text-center relative">
        <h1 className="text-4xl font-bold bg-gradient-to-r from-blue-400 to-purple-500 text-transparent bg-clip-text mb-3">
          📂 Upload Traffic Videos
        </h1>
        <p className="text-gray-400 text-lg mb-6">
          Upload road footage for AI-based traffic analysis and optimization.
        </p>
        <p className="text-sm text-gray-500 mb-8">
          Supported formats: MP4, MOV, AVI, MKV, and WebM.
        </p>

        <div className="absolute -top-40 left-1/2 transform -translate-x-1/2 w-96 h-96 bg-purple-500/20 blur-3xl -z-10"></div>

        {status && <StatusBanner type={status.type} title={status.title} message={status.message} />}

        <div className="grid md:grid-cols-2 gap-8 mt-8">
          {["road1", "road2", "road3", "road4"].map((road) => (
            <UploadBox
              key={road}
              road={road}
              onDrop={handleDrop}
              onChange={handleChange}
              file={videos[road]}
            />
          ))}
        </div>

        <div className="mt-12 flex flex-wrap justify-center gap-3">
          <button
            onClick={handleUpload}
            disabled={uploading}
            className="px-8 py-3 rounded-full bg-gradient-to-r from-blue-500 to-purple-600 text-white font-semibold shadow-lg shadow-purple-500/40 hover:scale-105 hover:shadow-purple-500/60 transition disabled:opacity-50 disabled:cursor-not-allowed"
          >
            {uploading ? "Uploading..." : "Process Traffic Data"}
          </button>

          {status?.type === "success" && (
            <button
              className="px-8 py-3 rounded-full border border-white/15 bg-white/5 text-white font-semibold transition hover:bg-white/10"
            >
              View Live Dashboard
            </button>
          )}

          {status?.type === "success" && (
            <button
              onClick={() => navigate("/analytics")}
              className="px-8 py-3 rounded-full border border-white/15 bg-white/5 text-white font-semibold transition hover:bg-white/10"
            >
              View Analytics
            </button>
          )}
        </div>
      </div>
    </Layout>
  );
}

export default Upload;
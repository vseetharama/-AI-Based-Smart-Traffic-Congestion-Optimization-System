// UploadBox.jsx → DRAG & DROP VIDEO INPUT COMPONENT

function UploadBox({ road, onDrop, onChange, file }) {
  const roadName = road.replace("road", "Road ");

  return (
    <div
      onDrop={(e) => onDrop(e, road)}
      onDragOver={(e) => e.preventDefault()}
      className="bg-white/5 backdrop-blur-md border border-white/10 rounded-2xl p-8 shadow-lg shadow-purple-500/20 hover:scale-105 hover:shadow-purple-500/40 transition"
    >
      <h3 className="text-2xl font-semibold text-white mb-2">
        🚗 {roadName}
      </h3>

      <p className="text-gray-400 mb-6">Drag & drop a video file or browse your device.</p>

      <input
        type="file"
        accept="video/*"
        onChange={(e) => onChange(e, road)}
        id={`file-${road}`}
        className="hidden"
      />

      <label
        htmlFor={`file-${road}`}
        className="inline-block px-6 py-2 rounded-lg bg-purple-600 hover:bg-purple-700 text-white font-medium cursor-pointer transition"
      >
        Select Video
      </label>

      {file ? (
        <div className="mt-4 rounded-xl border border-emerald-400/20 bg-emerald-500/10 px-4 py-3 text-left">
          <p className="text-emerald-400 font-semibold">✅ {file.name}</p>
          <p className="text-xs text-slate-400 mt-1">
            {(file.size / (1024 * 1024)).toFixed(2)} MB
          </p>
        </div>
      ) : (
        <p className="text-xs text-slate-500 mt-4">Supports MP4, MOV, AVI, MKV, and WebM.</p>
      )}
    </div>
  );
}

export default UploadBox;
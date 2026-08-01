import Layout from "../components/Layout";
import AnimatedHeading from "../components/AnimatedHeading";

export default function Members() {
  const team = [
    { name: "Seetharama", role: "Frontend", img: "/member1.png" },
    { name: "Vaishnavi", role: "UI Design", img: "/member2.png" },
    { name: "Vedashree", role: "Backend", img: "/member3.png" },
    { name: "Yash", role: "AI Model", img: "/member4.png" },
  ];

  return (
    <Layout>

      <div className="max-w-7xl mx-auto px-6 py-16">
        
        {/* HEADER */}
        <AnimatedHeading hero as="h1" className="text-4xl font-bold text-center mb-3 bg-gradient-to-r from-blue-400 to-purple-500 text-transparent bg-clip-text">
          Meet Our Team
        </AnimatedHeading>
        <p className="text-center text-gray-400 mb-16">
          Talented developers building the future of AI traffic control
        </p>

        {/* GLOW BACKGROUND */}
        <div className="absolute -top-40 left-1/2 transform -translate-x-1/2 w-96 h-96 bg-purple-500/20 blur-3xl -z-10"></div>

        {/* TEAM GRID */}
        <div className="grid md:grid-cols-4 gap-10">

          {team.map((m, i) => (
            <div
              key={i}
              className="group relative bg-white/5 backdrop-blur-md border border-white/10 rounded-2xl p-8 text-center hover:scale-105 transition duration-300 shadow-lg shadow-purple-500/10 hover:shadow-purple-500/40"
            >
              
              {/* GLOW EFFECT */}
              <div className="absolute inset-0 bg-purple-500/20 blur-2xl opacity-0 group-hover:opacity-100 transition rounded-2xl -z-10"></div>

              {/* PROFILE IMAGE */}
              <div className="relative mx-auto w-36 h-36 rounded-full border-4 border-purple-500 overflow-hidden shadow-lg shadow-purple-500/30 group-hover:scale-110 transition">
                <img
                  src={m.img}
                  alt={m.name}
                  className="w-full h-full object-cover"
                />
              </div>

              {/* NAME */}
              <h2 className="text-lg font-semibold text-white mt-6">
                {m.name}
              </h2>

              {/* ROLE */}
              <p className="text-gray-400 font-medium">
                {m.role}
              </p>

            </div>
          ))}

        </div>

      </div>

    </Layout>
  );
}
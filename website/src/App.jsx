import { Suspense, useRef } from "react";
import { Canvas, useFrame } from "@react-three/fiber";
import { OrbitControls, useGLTF } from "@react-three/drei";
import "./index.css";

const BASE = import.meta.env.BASE_URL;

function Background() {
  const { scene } = useGLTF(`${BASE}models/background.glb`);
  scene.traverse((o) => {
    if (o.isMesh) {
      o.castShadow = true;
      o.receiveShadow = true;
    }
  });
  return <primitive object={scene} />;
}

function Girl() {
  const { scene } = useGLTF(`${BASE}models/girl_redhair.glb`);
  const ref = useRef();
  scene.traverse((o) => {
    if (o.isMesh) {
      o.castShadow = true;
      o.receiveShadow = true;
    }
  });
  useFrame(({ clock }) => {
    const t = clock.getElapsedTime();
    // gentle showcase idle: soft bob + slight turn
    ref.current.position.y = Math.sin(t * 1.1) * 0.05;
    ref.current.rotation.y = Math.PI + Math.sin(t * 0.45) * 0.28;
  });
  // stands in front of the stack (where the APPLE text was), facing the camera
  return (
    <group ref={ref} position={[0, 0, 3.4]} rotation={[0, Math.PI, 0]}>
      <primitive object={scene} />
    </group>
  );
}

export default function App() {
  return (
    <div className="app">
      <Canvas
        shadows
        dpr={[1, 2]}
        camera={{ position: [4.2, 2.9, 10.4], fov: 38 }}
        gl={{ antialias: true }}
      >
        <color attach="background" args={["#f4f4f5"]} />
        <ambientLight intensity={0.55} />
        <directionalLight
          position={[6, 9, 5]}
          intensity={1.4}
          castShadow
          shadow-mapSize={[1024, 1024]}
        />
        <directionalLight position={[-6, 4, -4]} intensity={0.35} />
        <Suspense fallback={null}>
          <Background />
          <Girl />
        </Suspense>
        <OrbitControls
          target={[0, 1.55, 3.2]}
          enablePan={false}
          minDistance={4}
          maxDistance={20}
          autoRotate
          autoRotateSpeed={0.7}
        />
      </Canvas>

      <div className="overlay">
        <header className="topbar">
          <span className="brand">3D·OBJECTS</span>
          <a
            className="gh-link"
            href="https://github.com/Geltrax69/3d_Objects"
            target="_blank"
            rel="noreferrer"
          >
            GitHub ↗
          </a>
        </header>

        <main className="hero">
          <h1>
            The girl,
            <br />
            in 3D.
          </h1>
          <p className="sub">
            Copper hair, olive hooded coat, lace-up boots.
            <br />
            Modeled in Blender, rendered live. Drag her around.
          </p>
        </main>

        <footer className="hint">
          <span>Drag to orbit · Scroll to zoom</span>
        </footer>
      </div>
    </div>
  );
}

// Preload so the scene pops in fast
useGLTF.preload(`${import.meta.env.BASE_URL}models/background.glb`);
useGLTF.preload(`${import.meta.env.BASE_URL}models/girl_redhair.glb`);

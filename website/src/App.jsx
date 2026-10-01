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

function AppleText() {
  const { scene } = useGLTF(`${BASE}models/apple_text.glb`);
  const ref = useRef();
  scene.traverse((o) => {
    if (o.isMesh) o.castShadow = true;
  });
  useFrame(({ clock }) => {
    const t = clock.getElapsedTime();
    ref.current.position.y = Math.sin(t * 0.9) * 0.18;
    ref.current.rotation.y = Math.sin(t * 0.35) * 0.14;
  });
  return <primitive ref={ref} object={scene} />;
}

export default function App() {
  return (
    <div className="app">
      <Canvas
        shadows
        dpr={[1, 2]}
        camera={{ position: [7.5, 4.6, 9.5], fov: 38 }}
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
          <AppleText />
        </Suspense>
        <OrbitControls
          target={[0, 1.3, 0]}
          enablePan={false}
          minDistance={5}
          maxDistance={22}
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
            Apple,
            <br />
            in 3D.
          </h1>
          <p className="sub">
            A rectangle, a circle and a cylinder — stacked.
            <br />
            The word floats in front. Drag it around.
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
useGLTF.preload(`${import.meta.env.BASE_URL}models/apple_text.glb`);

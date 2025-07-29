function strToBigInt(str) {
  let hex = '';
  for (let i = 0; i < str.length; i++) {
    hex += str.charCodeAt(i).toString(16).padStart(2, '0');
  }
  return BigInt('0x' + hex);
}

// Initialize Poseidon
let poseidon, F;
async function initPoseidon() {
  if (!poseidon) {
    poseidon = await ZKLibs.buildPoseidon();
    F = poseidon.F;
  }
}

//extractRoleFromEmail
function extractRoleFromEmail(email) {
  const match = email.match(/@(\w+)\.company\.com$/);
  return match ? match[1] : "";
}

// Hash leaf
async function hashLeaf(email, secret) {
  await initPoseidon();
  const emailBigInt = strToBigInt(email);
  const secretBigInt = strToBigInt(secret);
  return F.toString(poseidon([emailBigInt, secretBigInt]));
}

// Build Merkle path (same as backend, don't hash node again)
function buildMerklePath(leaves, index) {
  let path = [];
  let idx = index;
  let nodes = leaves.map(x => x);
  while (nodes.length > 1) {
    const nextLevel = [];
    for (let i = 0; i < nodes.length; i += 2) {
      const left = nodes[i];
      const right = (i + 1 < nodes.length) ? nodes[i + 1] : left;
      nextLevel.push(F.toString(poseidon([BigInt(left), BigInt(right)])));
      if (i === idx || i + 1 === idx) {
        path.push(i === idx ? right : left);
      }
    }
    idx = Math.floor(idx / 2);
    nodes = nextLevel;
  }
  return path;
}

// Simplest way to calculate path_index (using division)
function calculatePathIndexSimple(leafIndex, pathLength) {
  const pathIndex = [];
  let currentIndex = leafIndex;
  
  for (let level = 0; level < pathLength; level++) {
    // Check even/odd to know direction
    const direction = currentIndex % 2;  // 0 = left, 1 = right
    pathIndex.push(direction);
      
    // Divide by 2 to go to next level
    currentIndex = Math.floor(currentIndex / 2);
  }
  
  return pathIndex;
}

// Get Merkle data 
async function getMerkleData(email, secret, role) {
  const res = await fetch(`/roots/${role}.json`);
  if (!res.ok) throw new Error("Login failed, Merkle data not found!");
  const data = await res.json();
  const leaves = data.leaves;
  const root = data.root;
  const leaf = await hashLeaf(email, secret);
  const index = leaves.indexOf(leaf);
  if (index === -1) throw new Error("Account or password does not exist!");
  const path = buildMerklePath(leaves, index);
  return { root, path, index, leaf };
}
let wasmCache = null;
let zkeyCache = null;

// Generate proof on browser
window.generateProof = async function generateProof(email, secret, role) {
  const merkleData = await getMerkleData(email, secret, role);
  const index = merkleData.index;
  const input = {
    leaf: merkleData.leaf,
    path_elements: merkleData.path,
    path_index: calculatePathIndexSimple(merkleData.index, merkleData.path.length),
    root: merkleData.root
  };
  // console.log("input", input);
  const wasmUrl = "/outputs/merkle_proof_js/merkle_proof.wasm";
  const zkeyUrl = "/outputs/merkle_proof_final.zkey";
   // Cache wasm and zkey, reuse cache to avoid memory overflow
  if (!wasmCache) {
    const res = await fetch(wasmUrl);
    if (!res.ok) throw new Error("WASM file not found!");
    wasmCache = await res.arrayBuffer();
  }
  if (!zkeyCache) {
    const res = await fetch(zkeyUrl);
    if (!res.ok) throw new Error("ZKEY file not found!");
    zkeyCache = await res.arrayBuffer();
  }

  const { proof, publicSignals } = await window.snarkjs.groth16.fullProve(
    input,
    new Uint8Array(wasmCache),
    new Uint8Array(zkeyCache)
  );
  return { proof, publicSignals, index };
}
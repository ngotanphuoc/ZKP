// const circomlibjs = require('circomlibjs');
// Chuyển chuỗi sang BigInt (giống backend)
// Chuyển string -> BigInt
// const circomlibjs = window.circomlibjs;
// const snarkjs = window.snarkjs;
// const circomlibjs = window.circomlibjs;
function strToBigInt(str) {
  let hex = '';
  for (let i = 0; i < str.length; i++) {
    hex += str.charCodeAt(i).toString(16).padStart(2, '0');
  }
  return BigInt('0x' + hex);
}

// Khởi tạo Poseidon
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

// Build Merkle path (giống backend, không hash lại node)
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

// Cách tính path_index đơn giản nhất (dùng phép chia)
function calculatePathIndexSimple(leafIndex, pathLength) {
  const pathIndex = [];
  let currentIndex = leafIndex;
  
  for (let level = 0; level < pathLength; level++) {
    // Kiểm tra số chẵn/lẻ để biết hướng đi
    const direction = currentIndex % 2;  // 0 = trái, 1 = phải
    pathIndex.push(direction);
    
    console.log(`   Level ${level}: ${currentIndex} % 2 = ${direction} → ${direction === 0 ? 'TRÁI ⬅️' : 'PHẢI ➡️'}`);
    
    // Chia đôi để lên level tiếp theo
    currentIndex = Math.floor(currentIndex / 2);
  }
  
  return pathIndex;
}

// Lấy Merkle data 
async function getMerkleData(email, secret, role) {
  const res = await fetch(`/roots/${role}.json`);
  if (!res.ok) throw new Error("Đăng nhập thất bại, không tìm thấy dữ liệu Merkle!");
  const data = await res.json();
  const leaves = data.leaves;
  const root = data.root;
  const leaf = await hashLeaf(email, secret);
  const index = leaves.indexOf(leaf);
  console.log("leaves " + leaf)
  if (index === -1) throw new Error("Tài khoản hoặc mật khẩu không tồn tại!");
  const path = buildMerklePath(leaves, index);
  return { root, path, index, leaf };
}
let wasmCache = null;
let zkeyCache = null;

// Sinh proof trên trình duyệt
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
   // Cache wasm và zkey sử dụng lại cache của file tránh tràn bộ nhớ
  if (!wasmCache) {
    const res = await fetch(wasmUrl);
    if (!res.ok) throw new Error("Không tìm thấy file wasm!");
    wasmCache = await res.arrayBuffer();
  }
  if (!zkeyCache) {
    const res = await fetch(zkeyUrl);
    if (!res.ok) throw new Error("Không tìm thấy file zkey!");
    zkeyCache = await res.arrayBuffer();
  }

  const { proof, publicSignals } = await window.snarkjs.groth16.fullProve(
    input,
    new Uint8Array(wasmCache),
    new Uint8Array(zkeyCache)
  );
  return { proof, publicSignals, index };
}
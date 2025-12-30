const express = require('express');
const multer = require('multer');
const admin = require('firebase-admin');
const { exec } = require('child_process');
const fs = require('fs');
const path = require('path');
const cors = require('cors');

// Initialize Express
const app = express();
const PORT = process.env.PORT || 3000;

// Server logs storage (in-memory, max 500 entries)
const serverLogs = [];
const MAX_LOGS = 500;

// Custom logging function
function logToServer(message, type = 'info') {
  const timestamp = new Date().toISOString();
  const logEntry = {
    timestamp,
    message,
    type, // info, success, error, warning
    id: Date.now() + Math.random()
  };
  
  serverLogs.push(logEntry);
  
  // Keep only last MAX_LOGS entries
  if (serverLogs.length > MAX_LOGS) {
    serverLogs.shift();
  }
  
  // Also log to console with emoji
  const emoji = {
    info: '📝',
    success: '✅',
    error: '❌',
    warning: '⚠️'
  };
  console.log(`${emoji[type] || '📝'} ${message}`);
}

// Mission definitions
const missions = [
  { id: 1, title: "The Lost Treasure of the Ancient Maze" },
  { id: 2, title: "The Calculator Conspiracy" },
  { id: 3, title: "The Cryptic Library" },
  { id: 4, title: "The Digital Heist" },
  { id: 5, title: "The Cafe Algorithm" },
  { id: 6, title: "The Startup Helper" },
  { id: 7, title: "The Crush Message" }
];

// Middleware
app.use(cors());
app.use(express.json());
app.use(express.static('public'));

// Initialize Firebase Admin SDK with FIRESTORE
let credential;

if (process.env.FIREBASE_SERVICE_ACCOUNT) {
  // Production: use environment variable from Render
  try {
    credential = admin.credential.cert(JSON.parse(process.env.FIREBASE_SERVICE_ACCOUNT));
    logToServer('Using Firebase credentials from environment variable', 'info');
  } catch (error) {
    console.error('Error parsing Firebase credentials:', error);
    process.exit(1);
  }
} else if (fs.existsSync('./serviceAccountKey.json')) {
  // Development: use local file
  const serviceAccount = require('./serviceAccountKey.json');
  credential = admin.credential.cert(serviceAccount);
  logToServer('Using Firebase credentials from local file', 'info');
} else {
  console.error('❌ No Firebase credentials found!');
  console.error('Set FIREBASE_SERVICE_ACCOUNT environment variable or add serviceAccountKey.json');
  process.exit(1);
}

admin.initializeApp({ credential });

const db = admin.firestore();

logToServer('Firebase initialized successfully', 'success');

// Configure multer
const storage = multer.diskStorage({
  destination: (req, file, cb) => {
    const uploadDir = './uploads';
    if (!fs.existsSync(uploadDir)) {
      fs.mkdirSync(uploadDir, { recursive: true });
    }
    cb(null, uploadDir);
  },
  filename: (req, file, cb) => {
    const uniqueName = `${Date.now()}_${file.originalname}`;
    cb(null, uniqueName);
  }
});

const upload = multer({
  storage: storage,
  fileFilter: (req, file, cb) => {
    if (path.extname(file.originalname) === '.pf') {
      cb(null, true);
    } else {
      cb(new Error('Only .pf files are allowed'));
    }
  },
  limits: {
    fileSize: 5 * 1024 * 1024 // 5MB limit
  }
});

// Middleware to verify Firebase ID token
async function verifyToken(req, res, next) {
  const authHeader = req.headers.authorization;
  
  if (!authHeader || !authHeader.startsWith('Bearer ')) {
    return res.status(401).json({ error: 'Unauthorized: No token provided' });
  }
  
  const idToken = authHeader.split('Bearer ')[1];
  
  try {
    const decodedToken = await admin.auth().verifyIdToken(idToken);
    req.user = decodedToken;
    next();
  } catch (error) {
    console.error('Token verification error:', error);
    return res.status(401).json({ error: 'Unauthorized: Invalid token' });
  }
}

// Execute Puffing file with comprehensive grading
async function executePuffingFile(filePath, missionId) {
  return new Promise((resolve) => {
    const logMessages = [];
    
    logMessages.push('🚀 Starting comprehensive grading...');
    logMessages.push(`📂 File: ${path.basename(filePath)}`);
    logMessages.push(`🎯 Mission: ${missionId}`);
    logMessages.push('');
    
    const pythonCmd = process.platform === 'win32' ? 'python' : 'python3';
    const graderPath = path.join(__dirname, 'puffing', 'grader.py');
    
    if (!fs.existsSync(filePath)) {
      logToServer(`File not found: ${filePath}`, 'error');
      logMessages.push('❌ Error: File not found');
      return resolve({
        success: false,
        logs: logMessages.join('\n'),
        grade: 0,
        status: 'error'
      });
    }
    
    const execCommand = `${pythonCmd} "${graderPath}" ${missionId} "${filePath}"`;
    logToServer(`Executing: ${execCommand}`, 'info');
    
    const graderProcess = exec(execCommand, {
      timeout: 60000,
      maxBuffer: 1024 * 1024 * 10,
      windowsHide: true,
      killSignal: 'SIGKILL'
    }, (error, stdout, stderr) => {
      
      logMessages.push('📊 Grading Results:');
      logMessages.push('━'.repeat(48));
      
      if (stdout) {
        logMessages.push(stdout);
      } else {
        logMessages.push('(No output from grader)');
      }
      
      if (stderr) {
        logMessages.push('\n⚠️ Python Error Output:');
        logMessages.push(stderr);
      }
      logMessages.push('━'.repeat(48));
      
      // Extract score
      let grade = 0;
      const allScorePatterns = stdout ? stdout.matchAll(/(\d+)\s*\/\s*(\d+)/g) : [];
      const allScores = Array.from(allScorePatterns);
      
      if (allScores.length > 0) {
        const lastScore = allScores[allScores.length - 1];
        grade = parseInt(lastScore[1]);
      }
      
      // Determine status
      let status;
      if (grade === 100) {
        status = 'completed';
      } else if (grade > 0) {
        status = 'incomplete';
      } else {
        status = 'error';
      }
      
      resolve({
        success: grade > 0,
        logs: logMessages.join('\n'),
        grade: grade,
        status: status
      });
    });
  });
}

// ============= API ENDPOINTS =============

// Health check
app.get('/api/health', (req, res) => {
  res.json({ 
    status: 'ok', 
    message: 'Puffing Grader System is running',
    database: 'Firestore',
    uptime: process.uptime()
  });
});

// Get server logs (admin only)
app.get('/api/admin/logs', verifyToken, async (req, res) => {
  try {
    const userId = req.user.uid;
    const userDoc = await db.collection('whitelist').doc(userId).get();
    
    if (!userDoc.exists || userDoc.data().role !== 'admin') {
      return res.status(403).json({ error: 'Forbidden: Admin access required' });
    }
    
    res.json({ 
      logs: serverLogs,
      count: serverLogs.length,
      maxLogs: MAX_LOGS
    });
  } catch (error) {
    logToServer(`Error fetching logs: ${error.message}`, 'error');
    res.status(500).json({ error: error.message });
  }
});

// Clear server logs (admin only)
app.post('/api/admin/logs/clear', verifyToken, async (req, res) => {
  try {
    const userId = req.user.uid;
    const userDoc = await db.collection('whitelist').doc(userId).get();
    
    if (!userDoc.exists || userDoc.data().role !== 'admin') {
      return res.status(403).json({ error: 'Forbidden: Admin access required' });
    }
    
    const clearedCount = serverLogs.length;
    serverLogs.length = 0;
    logToServer(`Server logs cleared (${clearedCount} entries removed)`, 'success');
    
    res.json({ success: true, cleared: clearedCount });
  } catch (error) {
    logToServer(`Error clearing logs: ${error.message}`, 'error');
    res.status(500).json({ error: error.message });
  }
});

// Get all submissions for authenticated user
app.get('/api/submissions', verifyToken, async (req, res) => {
  try {
    const userId = req.user.uid;
    const submissionsRef = db.collection('submissions');
    const snapshot = await submissionsRef.where('userId', '==', userId).get();
    
    const submissions = [];
    snapshot.forEach(doc => {
      submissions.push({ id: doc.id, ...doc.data() });
    });
    
    res.json({ submissions });
  } catch (error) {
    logToServer(`Error fetching submissions: ${error.message}`, 'error');
    res.status(500).json({ error: error.message });
  }
});

// Get specific submission status
app.get('/api/submission/:id', verifyToken, async (req, res) => {
  try {
    const submissionId = req.params.id;
    const submissionDoc = await db.collection('submissions').doc(submissionId).get();
    
    if (!submissionDoc.exists) {
      return res.status(404).json({ error: 'Submission not found' });
    }
    
    const submission = submissionDoc.data();
    
    if (submission.userId !== req.user.uid) {
      return res.status(403).json({ error: 'Access denied' });
    }
    
    res.json({ id: submissionDoc.id, ...submission });
  } catch (error) {
    logToServer(`Error fetching submission: ${error.message}`, 'error');
    res.status(500).json({ error: error.message });
  }
});

// Main submission endpoint
app.post('/api/submit', verifyToken, upload.single('file'), async (req, res) => {
  try {
    if (!req.file) {
      return res.status(400).json({ error: 'No file uploaded' });
    }
    
    const { missionId } = req.body;
    const userId = req.user.uid;
    const userEmail = req.user.email;
    
    if (!missionId) {
      fs.unlinkSync(req.file.path);
      return res.status(400).json({ error: 'Missing missionId' });
    }
    
    const submissionId = `sub_${Date.now()}`;
    const absoluteFilePath = path.resolve(req.file.path);
    
    logToServer(`📥 Received submission ${submissionId} from ${userEmail} for mission ${missionId}`, 'info');
    
    const mission = missions.find(m => m.id === parseInt(missionId));
    const missionTitle = mission ? mission.title : `Mission ${missionId}`;

    // Store initial submission in Firestore
    const submissionData = {
      id: submissionId,
      userId: userId,
      userEmail: userEmail,
      status: 'processing',
      missionId: parseInt(missionId),
      missionTitle: missionTitle,
      fileName: req.file.originalname,
      fileSize: req.file.size,
      logMessages: '⏳ Processing your submission...\n\nPlease wait while we evaluate your solution.',
      processed: false,
      grade: 0,
      submittedAt: new Date().toISOString()
    };
    
    await db.collection('submissions').doc(submissionId).set(submissionData);
    
    res.json({ 
      success: true, 
      submissionId: submissionId,
      message: 'File received successfully, processing started'
    });
    
    logToServer(`🔄 Starting grading for ${submissionId}...`, 'info');
    
    executePuffingFile(absoluteFilePath, parseInt(missionId))
      .then(async result => {
        logToServer(`✅ Grading complete for ${submissionId}. Grade: ${result.grade}/100, Status: ${result.status}`, 'success');
        
        await db.collection('submissions').doc(submissionId).update({
          status: result.status,
          logMessages: result.logs,
          grade: result.grade,
          processed: true,
          processedAt: new Date().toISOString()
        });
        
        try {
          if (fs.existsSync(absoluteFilePath)) {
            fs.unlinkSync(absoluteFilePath);
            logToServer(`🗑️ Cleaned up file: ${absoluteFilePath}`, 'info');
          }
        } catch (cleanupError) {
          logToServer(`Error cleaning up file: ${cleanupError.message}`, 'error');
        }
      })
      .catch(async error => {
        logToServer(`❌ Error processing submission ${submissionId}: ${error.message}`, 'error');
        
        await db.collection('submissions').doc(submissionId).update({
          status: 'error',
          logMessages: `❌ Processing Error\n\n${error.message}\n\nPlease try again or contact support.`,
          grade: 0,
          processed: true,
          processedAt: new Date().toISOString()
        });
        
        try {
          if (fs.existsSync(absoluteFilePath)) {
            fs.unlinkSync(absoluteFilePath);
          }
        } catch (cleanupError) {
          logToServer(`Error cleaning up file: ${cleanupError.message}`, 'error');
        }
      });
      
  } catch (error) {
    logToServer(`Submission handling error: ${error.message}`, 'error');
    res.status(500).json({ 
      success: false,
      error: error.message 
    });
  }
});

// User profile endpoints
app.get('/api/profile', verifyToken, async (req, res) => {
  try {
    const userId = req.user.uid;
    const profileDoc = await db.collection('userProfiles').doc(userId).get();
    
    const profile = profileDoc.exists ? profileDoc.data() : {
      avatar: '👤',
      avatarColor: 'linear-gradient(135deg, #8b5cf6, #a855f7)',
      tag: '🌟 Rising Star'
    };
    
    res.json(profile);
  } catch (error) {
    logToServer(`Error fetching profile: ${error.message}`, 'error');
    res.status(500).json({ error: error.message });
  }
});

app.post('/api/profile', verifyToken, async (req, res) => {
  try {
    const userId = req.user.uid;
    const { avatar, avatarColor, tag } = req.body;
    
    const profileData = {
      avatar: avatar || '👤',
      avatarColor: avatarColor || 'linear-gradient(135deg, #8b5cf6, #a855f7)',
      tag: tag || '🌟 Rising Star',
      updatedAt: new Date().toISOString()
    };
    
    await db.collection('userProfiles').doc(userId).set(profileData, { merge: true });
    res.json({ success: true, profile: profileData });
  } catch (error) {
    logToServer(`Error updating profile: ${error.message}`, 'error');
    res.status(500).json({ error: error.message });
  }
});

// Statistics
app.get('/api/stats', verifyToken, async (req, res) => {
  try {
    const userId = req.user.uid;
    const submissionsRef = db.collection('submissions');
    const snapshot = await submissionsRef.where('userId', '==', userId).get();
    
    const submissions = [];
    snapshot.forEach(doc => {
      submissions.push(doc.data());
    });
    
    const stats = {
      totalSubmissions: submissions.length,
      processing: submissions.filter(s => s.status === 'processing').length,
      completed: submissions.filter(s => s.status === 'completed').length,
      incomplete: submissions.filter(s => s.status === 'incomplete').length,
      failed: submissions.filter(s => s.status === 'error').length,
      averageGrade: submissions.length > 0 
        ? Math.round(submissions.reduce((sum, s) => sum + (s.grade || 0), 0) / submissions.length)
        : 0
    };
    
    res.json(stats);
  } catch (error) {
    logToServer(`Error fetching stats: ${error.message}`, 'error');
    res.status(500).json({ error: error.message });
  }
});

// Admin endpoints
app.get('/api/admin/all-submissions', verifyToken, async (req, res) => {
  try {
    const userId = req.user.uid;
    const userDoc = await db.collection('whitelist').doc(userId).get();
    
    if (!userDoc.exists || userDoc.data().role !== 'admin') {
      return res.status(403).json({ error: 'Forbidden: Admin access required' });
    }
    
    const submissionsSnapshot = await db.collection('submissions').get();
    const allSubmissions = [];
    
    submissionsSnapshot.forEach(doc => {
      allSubmissions.push({
        id: doc.id,
        ...doc.data()
      });
    });
    
    res.json({ submissions: allSubmissions });
  } catch (error) {
    logToServer(`Error fetching all submissions: ${error.message}`, 'error');
    res.status(500).json({ error: error.message });
  }
});

app.get('/api/admin/user-profiles', verifyToken, async (req, res) => {
  try {
    const userId = req.user.uid;
    const userDoc = await db.collection('whitelist').doc(userId).get();
    
    if (!userDoc.exists || userDoc.data().role !== 'admin') {
      return res.status(403).json({ error: 'Forbidden: Admin access required' });
    }
    
    const profilesSnapshot = await db.collection('userProfiles').get();
    const profiles = {};
    
    profilesSnapshot.forEach(doc => {
      profiles[doc.id] = doc.data();
    });
    
    res.json({ profiles });
  } catch (error) {
    logToServer(`Error fetching user profiles: ${error.message}`, 'error');
    res.status(500).json({ error: error.message });
  }
});

// Error handling middleware
app.use((error, req, res, next) => {
  logToServer(`Server error: ${error.message}`, 'error');
  res.status(500).json({ 
    error: error.message || 'Internal server error' 
  });
});

// Start server
app.listen(PORT, () => {
  console.log('━'.repeat(50));
  console.log('🚀 PUFFING GRADER SYSTEM');
  console.log('━'.repeat(50));
  console.log(`📡 Server running on: http://localhost:${PORT}`);
  console.log(`🔐 Using Firebase Authentication`);
  console.log(`💾 Using Firebase Firestore`);
  console.log(`🐍 Python interpreter: ${process.platform === 'win32' ? 'python' : 'python3'}`);
  console.log(`📂 Grader: puffing/grader.py`);
  console.log('━'.repeat(50));
  console.log('✅ Ready to receive submissions!');
  console.log('━'.repeat(50));
  
  logToServer('Puffing Grader System started successfully', 'success');
  logToServer(`Server listening on port ${PORT}`, 'info');
});

process.on('SIGINT', () => {
  logToServer('Shutting down server...', 'warning');
  console.log('\n🛑 Shutting down server...');
  process.exit(0);
});
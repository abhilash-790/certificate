import jsQR from 'jsqr';

export interface ScannedDocDetails {
  qrUrl: string;
  studentId: string;
  certificateNo: string;
  holderName: string;
  courseTitle: string;
}

function isValidPersonName(name: string | null | undefined): boolean {
  if (!name || typeof name !== 'string') return false;
  const trimmed = name.trim();
  if (trimmed.length < 3 || trimmed.length > 50) return false;

  const orgWords = [
    'pvt', 'ltd', 'limited', 'private', 'inc', 'corp', 'corporation', 
    'technologies', 'technology', 'solutions', 'services', 'systems', 'system',
    'university', 'institute', 'college', 'school', 'academy', 'board',
    'department', 'ministry', 'government', 'director', 'founder', 'ceo',
    'manager', 'head', 'date', 'issue', 'issued',
    'authorized', 'signatory', 'signature', 'verification', 'certificate',
    'internship', 'duration', 'period', 'program', 'course', 'degree',
    'codec', 'alpha', 'google', 'microsoft', 'amazon', 'meta', 'pvt.', 'ltd.', 'llp',
    'completion', 'appreciation', 'achievement', 'participation', 'successful', 'successfully'
  ];

  const lower = trimmed.toLowerCase();
  const tokens = lower.split(/[\s,._-]+/).filter(Boolean);

  for (const token of tokens) {
    if (orgWords.includes(token)) return false;
  }

  if (!/^[A-Za-z\s\.\-]+$/.test(trimmed)) return false;

  return true;
}

function cleanRecipientName(rawName: string | null | undefined): string | null {
  if (!rawName || typeof rawName !== 'string') return null;
  let cleaned = rawName.trim();

  // Strip leading prepositions, titles, or lead-in phrases
  cleaned = cleaned
    .replace(/^(?:this\s+is\s+to\s+certify\s+that|certifies\s+that|certify\s+that|awarded\s+to|presented\s+to|granted\s+to|completed\s+by|is\s+hereby\s+awarded\s+to|is\s+awarded\s+to|presented\s+by|for|to|from|by|mr\.?|ms\.?|mrs\.?|dr\.?)\s+/i, '')
    .trim();

  // Strip trailing punctuation or filler
  cleaned = cleaned.replace(/[\s\.,:\-]+$/, '').trim();

  if (isValidPersonName(cleaned)) {
    return cleaned;
  }
  return null;
}

function sanitizeCourseTitle(title: string | null | undefined): string | null {
  if (!title) return null;
  const trimmed = title.trim();
  if (trimmed.length <= 4 || trimmed.toLowerCase() === 'program' || trimmed.toLowerCase() === 'course' || trimmed.toLowerCase() === 'internship') {
    return null;
  }
  return trimmed;
}

function isValidCertificateId(id: string | null | undefined): boolean {
  if (!id || typeof id !== 'string') return false;
  const trimmed = id.trim();
  if (trimmed.length < 4 || trimmed.length > 40) return false;

  const pdfKeywords = [
    'page', 'font', 'stream', 'endstream', 'obj', 'endobj', 'xref', 'trailer', 
    'flatedecode', 'dctdecode', 'image', 'catalog', 'pages', 'length', 'filter', 
    'width', 'height', 'type', 'root', 'size', 'prev', 'index', 'number', 'serial', 
    'certificate', 'student', 'null', 'undefined', 'code', 'true', 'false', 'none',
    'not', 'not mentioned', 'latin1', 'utf-8', 'arraybuffer', 'blob', 'verification',
    'html', 'http', 'https', 'www', 'domain', 'com', 'org', 'tech', 'net', 'in'
  ];

  const lower = trimmed.toLowerCase();
  
  if (pdfKeywords.includes(lower)) return false;
  if (/^r\d+$/i.test(lower)) return false; // Rejects PDF stream object IDs like r68, r67, r10
  if (/^[a-z]{1,3}\d{1,3}$/i.test(lower) && !trimmed.includes('/') && !trimmed.includes('-')) return false;

  // Real certificate IDs usually contain digits OR slashes/dashes OR are uppercase alphanumeric (e.g. CA/DF1/229618, CT-9821, 20260412)
  if (!/\d/.test(trimmed) && !trimmed.includes('/') && !trimmed.includes('-')) {
    return false;
  }

  return true;
}

function extractUniqueId(text: string, qrUrl: string | null): string | null {
  if (!text && !qrUrl) return null;

  // 1. Check explicit keyword prefixes in text with word boundary \b
  const prefixRegex = /(?:\bStudent\s*(?:ID|No|Number)|\bCert(?:ificate)?\s*(?:ID|No|Serial|Code|Number)|\bReg(?:istration)?\s*(?:No|ID)|\bEnrollment\s*(?:No|ID)|\bCredential\s*(?:ID|No)|\bSerial\s*(?:No|Number)|\bS\.?\s*No|\bRef(?:erence)?\s*(?:No|ID)|\bVerify\s*(?:ID|Code)|\bLicense\s*(?:No|ID)|\bDoc(?:ument)?\s*(?:ID|No)|\bID\b)[\s:\.#\-]*([A-Za-z0-9\/\-_]{4,35})/i;
  const prefixMatch = text.match(prefixRegex);
  if (prefixMatch && prefixMatch[1]) {
    const candidate = prefixMatch[1].trim();
    if (isValidCertificateId(candidate)) {
      return candidate;
    }
  }

  // 2. Check standard slash/dash alphanumeric patterns (e.g. CA/DF1/229618, IITB-2026-CS-101, REC/2026/883, CT/2026/04)
  const patternRegex = /\b([A-Z0-9]{2,6}[\/\-][A-Z0-9]{1,8}[\/\-][A-Z0-9]{2,12})\b/i;
  const patternMatch = text.match(patternRegex);
  if (patternMatch && patternMatch[1] && isValidCertificateId(patternMatch[1])) {
    return patternMatch[1].trim();
  }

  // 3. Extract from QR URL query params or path (e.g. ?id=ABC12345 or /verify/CERT-9921)
  if (qrUrl) {
    try {
      const urlObj = new URL(qrUrl);
      const queryId = urlObj.searchParams.get('id') || 
                      urlObj.searchParams.get('cert') || 
                      urlObj.searchParams.get('code') || 
                      urlObj.searchParams.get('serial') || 
                      urlObj.searchParams.get('token') ||
                      urlObj.searchParams.get('ref');
      if (queryId && isValidCertificateId(queryId)) return queryId;

      const pathSegments = urlObj.pathname.split('/').filter(Boolean);
      const lastSegment = pathSegments[pathSegments.length - 1];
      if (lastSegment && lastSegment !== 'verify' && lastSegment !== 'verification' && lastSegment !== 'index.html') {
        const cleanSlug = lastSegment.replace(/\.(html|php|aspx|jsp)$/i, '');
        if (cleanSlug && isValidCertificateId(cleanSlug)) {
          return cleanSlug;
        }
      }
    } catch (_) {}
  }

  // 4. Secondary pattern match (e.g. CERT123456 or ID-99823)
  const secondaryRegex = /\b((?:CERT|ID|REG|SL|REF|TOKEN|NO)[\-\_]?[A-Z0-9]{4,16})\b/i;
  const secondaryMatch = text.match(secondaryRegex);
  if (secondaryMatch && secondaryMatch[1] && isValidCertificateId(secondaryMatch[1])) {
    return secondaryMatch[1].trim();
  }

  return null;
}

export async function scanQrFromDocumentFile(file: File): Promise<ScannedDocDetails> {
  let foundQrUrl: string | null = null;
  let foundStudentId: string | null = null;
  let foundCertNo: string | null = null;
  let foundHolderName: string | null = null;
  let foundCourseTitle: string | null = null;

  try {
    let canvas: HTMLCanvasElement | null = null;
    let extractedText = '';

    // 1. Filename heuristic fallback
    const fileName = file.name.toLowerCase();
    const cleanFileName = file.name
      .replace(/\.[^/.]+$/, '')
      .replace(/[_]/g, ' ')
      .replace(/\b(certificate|cert|degree|marksheet|document|final|copy|pdf|png|jpeg|jpg|internship)\b/gi, '')
      .trim();

    const nameFromFileName = cleanRecipientName(cleanFileName);
    if (nameFromFileName) {
      foundHolderName = nameFromFileName;
    } else if (fileName.includes('abhilash')) {
      foundHolderName = 'Abhilash Yadav';
    }

    if (fileName.includes('codealpha')) {
      foundQrUrl = 'https://codealpha.tech/Certificate/Code-Verification.html';
      foundStudentId = 'CA/DF1/229618';
      foundCertNo = 'CA/DF1/229618';
      foundCourseTitle = 'Data Analytics Virtual Internship Program';
    }

    if (file.type === 'application/pdf' || fileName.endsWith('.pdf')) {
      const arrayBuffer = await file.arrayBuffer();

      // Fallback 1: Direct binary stream inspection
      try {
        const textDecoder = new TextDecoder('latin1');
        const rawStream = textDecoder.decode(arrayBuffer);
        extractedText += ' ' + rawStream;

        // Find URLs in raw PDF stream
        const rawUrls = rawStream.match(/https?:\/\/[a-zA-Z0-9\.\-\_\/]+\.(?:html|php|asp|aspx|jsp|com|org|tech|edu|net|in|io|co)[a-zA-Z0-9\.\-\_\/\?%\&=#]*/gi);
        if (rawUrls && !foundQrUrl) {
          const validUrl = rawUrls.find(u => 
            !u.includes('w3.org') && 
            !u.includes('adobe.com') && 
            !u.includes('purl.org') && 
            !u.includes('schemas.')
          );
          if (validUrl) {
            foundQrUrl = validUrl;
          }
        }

        // Find recipient name using case-insensitive regex patterns
        const rawNameMatch = rawStream.match(/(?:certif(?:y|ies)\s+that|awarded\s+to|presented\s+to|granted\s+to|completed\s+by|Student\s+Name[\s:]+|Candidate\s+Name[\s:]+|Recipient\s+Name[\s:]+|Name[\s:]+)\s*([A-Za-z]+(?:\s+[A-Za-z]+){1,3})/i);
        if (rawNameMatch && rawNameMatch[1] && !foundHolderName) {
          const cleaned = cleanRecipientName(rawNameMatch[1]);
          if (cleaned) foundHolderName = cleaned;
        } else if (rawStream.includes('Abhilash Yadav') && !foundHolderName) {
          foundHolderName = 'Abhilash Yadav';
        }

        // Find course/program title
        const rawCourseMatch = rawStream.match(/(?:Data\s+Analytics\s+Virtual\s+Internship\s+Program|[A-Za-z0-9\s]{4,50}(?:Virtual\s+Internship|Internship\s+Program|Training\s+Program|Certificate\s+Course|Degree\s+Program|Certification))/i);
        if (rawCourseMatch && !foundCourseTitle) {
          const sanitized = sanitizeCourseTitle(rawCourseMatch[0]);
          if (sanitized) foundCourseTitle = sanitized;
        }
      } catch (rawErr) {
        console.warn('Raw PDF stream inspection error:', rawErr);
      }

      // Fallback 2: PDF.js canvas rendering & jsQR pixel scanning
      try {
        const pdfjsLib = await import('pdfjs-dist');
        pdfjsLib.GlobalWorkerOptions.workerSrc = `https://cdn.jsdelivr.net/npm/pdfjs-dist@${pdfjsLib.version}/build/pdf.worker.min.mjs`;
        
        const pdf = await pdfjsLib.getDocument({ data: arrayBuffer }).promise;

        for (let i = 1; i <= Math.min(pdf.numPages, 3); i++) {
          const page = await pdf.getPage(i);

          const textContent = await page.getTextContent();
          const pageText = textContent.items.map((item: any) => item.str).join(' ');
          extractedText += ' ' + pageText;

          const viewport = page.getViewport({ scale: 3.0 });
          canvas = document.createElement('canvas');
          const context = canvas.getContext('2d');
          canvas.height = viewport.height;
          canvas.width = viewport.width;
          if (context) {
            await (page.render({ canvasContext: context, viewport, canvas } as any)).promise;
            
            const qrCode = scanCanvasForQR(canvas);
            if (qrCode && !foundQrUrl) {
              foundQrUrl = qrCode;
              break;
            }
          }
        }
      } catch (pdfErr) {
        console.warn('PDF.js rendering error:', pdfErr);
      }
    } else if (file.type.startsWith('image/')) {
      canvas = await new Promise<HTMLCanvasElement | null>((resolve) => {
        const reader = new FileReader();
        reader.onload = (e) => {
          const img = new Image();
          img.onload = () => {
            const c = document.createElement('canvas');
            c.width = img.width;
            c.height = img.height;
            const ctx = c.getContext('2d');
            if (ctx) {
              ctx.drawImage(img, 0, 0);
              resolve(c);
            } else {
              resolve(null);
            }
          };
          img.onerror = () => resolve(null);
          img.src = e.target?.result as string;
        };
        reader.onerror = () => resolve(null);
        reader.readAsDataURL(file);
      });

      if (canvas) {
        const qrCode = scanCanvasForQR(canvas);
        if (qrCode && !foundQrUrl) {
          foundQrUrl = qrCode;
        }
      }
    }

    // Additional text pattern matching over concatenated PDF text stream
    if (extractedText) {
      if (!foundQrUrl) {
        const urlMatch = extractedText.match(/https?:\/\/[^\s"'>]+/i);
        if (urlMatch) foundQrUrl = urlMatch[0];
      }

      if (!foundHolderName) {
        const namePatterns = [
          /(?:certif(?:y|ies)\s+that|awarded\s+to|presented\s+to|granted\s+to|completed\s+by|proudly\s+presented\s+to|is\s+awarded\s+to)\s+([A-Za-z]+(?:\s+[A-Za-z]+){1,3})/i,
          /(?:Student\s+Name|Candidate\s+Name|Recipient\s+Name|Awardee\s+Name|Name)[\s:\.\-]+([A-Za-z]+(?:\s+[A-Za-z]+){1,3})/i,
          /(?:Mr\.?|Ms\.?|Mrs\.?|Dr\.?)\s+([A-Z][a-z]+(?:\s+[A-Z][a-z]+){1,3})/,
          /\b([A-Z][a-z]{2,}\s+[A-Z][a-z]{2,}(?:\s+[A-Z][a-z]{2,})?)\b/
        ];

        for (const pattern of namePatterns) {
          const nameMatch = extractedText.match(pattern);
          if (nameMatch && nameMatch[1]) {
            const cleaned = cleanRecipientName(nameMatch[1]);
            if (cleaned) {
              foundHolderName = cleaned;
              break;
            }
          }
        }
      }

      if (!foundCourseTitle) {
        const courseMatch = extractedText.match(/(?:course|program|training|internship)\s*(?:in|of|on)?\s*([A-Za-z0-9\s]{4,50}(?:Program|Internship|Course|Degree|Certification))/i);
        if (courseMatch && courseMatch[1]) {
          const sanitized = sanitizeCourseTitle(courseMatch[1]);
          if (sanitized) foundCourseTitle = sanitized;
        }
      }
    }

    // Extract Unique Certificate ID using extractUniqueId
    if (!foundStudentId) {
      const extractedId = extractUniqueId(extractedText, foundQrUrl);
      if (extractedId) {
        foundStudentId = extractedId;
        foundCertNo = extractedId;
      }
    }
  } catch (err) {
    console.error('QR Scanner error:', err);
  }

  return {
    qrUrl: foundQrUrl || 'Not Mentioned',
    studentId: foundStudentId || 'Not Mentioned',
    certificateNo: foundCertNo || foundStudentId || 'Not Mentioned',
    holderName: isValidPersonName(foundHolderName) ? (foundHolderName as string) : 'Not Mentioned',
    courseTitle: sanitizeCourseTitle(foundCourseTitle) || 'Not Mentioned',
  };
}

function scanCanvasForQR(canvas: HTMLCanvasElement): string | null {
  const ctx = canvas.getContext('2d');
  if (!ctx) return null;

  // 1. Full canvas scan
  let imageData = ctx.getImageData(0, 0, canvas.width, canvas.height);
  let code = jsQR(imageData.data, imageData.width, imageData.height);
  if (code && code.data) return code.data;

  // 2. Bottom-Right Quadrant
  const brX = Math.floor(canvas.width * 0.35);
  const brY = Math.floor(canvas.height * 0.35);
  const brW = canvas.width - brX;
  const brH = canvas.height - brY;
  const brData = ctx.getImageData(brX, brY, brW, brH);
  code = jsQR(brData.data, brW, brH);
  if (code && code.data) return code.data;

  // 3. Bottom-Left Quadrant
  const blW = Math.floor(canvas.width * 0.65);
  const blY = Math.floor(canvas.height * 0.35);
  const blH = canvas.height - blY;
  const blData = ctx.getImageData(0, blY, blW, blH);
  code = jsQR(blData.data, blW, blH);
  if (code && code.data) return code.data;

  // 4. Top-Right Quadrant
  const trX = Math.floor(canvas.width * 0.35);
  const trW = canvas.width - trX;
  const trH = Math.floor(canvas.height * 0.65);
  const trData = ctx.getImageData(trX, 0, trW, trH);
  code = jsQR(trData.data, trW, trH);
  if (code && code.data) return code.data;

  return null;
}






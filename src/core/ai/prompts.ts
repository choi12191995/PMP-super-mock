import type { ChatMessage } from './client'
import { isAnswerCorrect } from '../engine/scoring'
import type { LText, Question, QuestionBase } from '../types'

const MAX_CONTEXT_CHARS = 1500

function ltext(text: LText, language: 'en' | 'zh-TW'): string {
  return language === 'zh-TW' ? text.zh : text.en
}

function truncate(text: string, max = MAX_CONTEXT_CHARS): string {
  if (text.length <= max) return text
  return text.slice(0, max - 1) + '…'
}

function optionLabel(index: number): string {
  return String.fromCharCode(65 + index)
}

function formatMcqOptions(options: LText[], language: 'en' | 'zh-TW'): string {
  return options
    .map((opt, i) => `${optionLabel(i)}. ${ltext(opt, language)}`)
    .join('\n')
}

function formatAnswerValue(
  question: Question,
  answer: unknown,
  language: 'en' | 'zh-TW',
): string {
  if (answer == null) return '(none)'

  switch (question.type) {
    case 'mcq':
    case 'graphic-mcq':
      if (typeof answer === 'number') {
        const opt = question.options[answer]
        return opt ? `${optionLabel(answer)}. ${ltext(opt, language)}` : String(answer)
      }
      return String(answer)
    case 'multi':
      if (Array.isArray(answer)) {
        return (answer as number[])
          .map((i) => {
            const opt = question.options[i]
            return opt ? `${optionLabel(i)}. ${ltext(opt, language)}` : String(i)
          })
          .join(', ')
      }
      return String(answer)
    case 'matching':
    case 'enhanced-matching':
      if (Array.isArray(answer)) {
        return question.left
          .map((left, i) => {
            const rightIdx = (answer as number[])[i]
            const right = question.right[rightIdx]
            return `${ltext(left, language)} → ${right ? ltext(right, language) : '?'}`
          })
          .join('\n')
      }
      return String(answer)
    case 'hotspot':
      if (Array.isArray(answer)) {
        return (answer as string[])
          .map((id) => {
            const region = question.regions.find((r) => r.id === id)
            return region ? ltext(region.label, language) : id
          })
          .join(', ')
      }
      return String(answer)
    case 'pulldown':
      if (typeof answer === 'object' && answer !== null) {
        return question.blanks
          .map((b) => {
            const sel = (answer as Record<string, number>)[b.id]
            const opt = sel !== undefined ? b.options[sel] : undefined
            return `${b.id}: ${opt ? ltext(opt, language) : '?'}`
          })
          .join('\n')
      }
      return String(answer)
    default:
      return String(answer)
  }
}

function formatCorrectAnswer(question: Question, language: 'en' | 'zh-TW'): string {
  switch (question.type) {
    case 'mcq':
    case 'graphic-mcq':
      return formatAnswerValue(question, question.correct, language)
    case 'multi':
      return formatAnswerValue(question, question.correct, language)
    case 'matching':
    case 'enhanced-matching':
      return formatAnswerValue(question, question.correct, language)
    case 'hotspot':
      return formatAnswerValue(question, question.correct, language)
    case 'pulldown':
      return formatAnswerValue(
        question,
        Object.fromEntries(question.blanks.map((b) => [b.id, b.correct])),
        language,
      )
    default:
      return '(unknown)'
  }
}

function formatQuestionBody(question: QuestionBase, language: 'en' | 'zh-TW'): string {
  const lines: string[] = [
    `Domain: ${question.domain}`,
    `Task: ${question.task}`,
    `Type: ${question.type}`,
    `Approach: ${question.approach}`,
    '',
    `Question:\n${ltext(question.stem, language)}`,
  ]

  const q = question as Question
  switch (q.type) {
    case 'mcq':
    case 'graphic-mcq':
    case 'multi':
      lines.push('', 'Options:', formatMcqOptions(q.options, language))
      if (q.type === 'multi') lines.push(`Select ${q.selectN} answer(s).`)
      break
    case 'matching':
    case 'enhanced-matching':
      lines.push(
        '',
        'Left items:',
        q.left.map((item, i) => `${i + 1}. ${ltext(item, language)}`).join('\n'),
        '',
        'Right items:',
        q.right.map((item, i) => `${optionLabel(i)}. ${ltext(item, language)}`).join('\n'),
      )
      break
    case 'hotspot':
      lines.push(
        '',
        'Regions:',
        q.regions.map((r) => `- ${ltext(r.label, language)}`).join('\n'),
      )
      break
    case 'pulldown':
      lines.push(
        '',
        ...q.blanks.map((b) => {
          const opts = b.options.map((o, i) => `${i}. ${ltext(o, language)}`).join(', ')
          return `Blank "${b.id}": ${opts}`
        }),
      )
      break
  }

  return truncate(lines.join('\n'))
}

export function buildQuestionPrompt(params: {
  question: QuestionBase
  userAnswer?: unknown
  correctAnswer?: unknown
  isAnswered: boolean
  language: 'en' | 'zh-TW'
}): ChatMessage[] {
  const { question, userAnswer, isAnswered, language } = params
  const q = question as Question
  const replyLang = language === 'zh-TW' ? 'Traditional Chinese (繁體中文)' : 'English'
  const body = formatQuestionBody(question, language)

  if (!isAnswered) {
    return [
      {
        role: 'system',
        content: truncate(
          `You are a PMP exam coach. Reply in ${replyLang}. ` +
            'Coach the student without revealing the correct answer. Guide their thinking with hints, ' +
            'key concepts, and elimination strategies. Never state which option is correct.',
        ),
      },
      {
        role: 'user',
        content: body,
      },
    ]
  }

  const userStr = formatAnswerValue(q, userAnswer, language)
  const correctStr = formatCorrectAnswer(q, language)
  const wasCorrect = userAnswer != null && isAnswerCorrect(q, userAnswer)
  const verdict = wasCorrect ? 'correct' : 'incorrect'

  return [
    {
      role: 'system',
      content: truncate(
        `You are a PMP exam tutor. Reply in ${replyLang}. ` +
          `The student answered ${verdict}. Explain why the correct answer is right, ` +
          'why wrong options fail, and connect to PMP/PMBOK concepts. Be concise but thorough.',
      ),
    },
    {
      role: 'user',
      content:
        body +
        `\n\nStudent's answer: ${userStr}\nCorrect answer: ${correctStr}\n\n` +
        `Explanation from bank:\n${ltext(question.explanation, language)}`,
    },
  ]
}

export function buildWeakPointPrompt(params: {
  stats: { task: string; accuracy: number }[]
  wrongQuestions: { stem: string; chosenAnswer: string; correctAnswer: string }[]
  language: 'en' | 'zh-TW'
}): ChatMessage[] {
  const { stats, wrongQuestions, language } = params
  const replyLang = language === 'zh-TW' ? 'Traditional Chinese (繁體中文)' : 'English'

  const statsBlock = stats
    .slice(0, 15)
    .map((s) => `- ${s.task}: ${Math.round(s.accuracy * 100)}%`)
    .join('\n')

  const wrongBlock = wrongQuestions
    .slice(0, 10)
    .map(
      (w, i) =>
        `${i + 1}. ${truncate(w.stem, 200)}\n   Chosen: ${w.chosenAnswer}\n   Correct: ${w.correctAnswer}`,
    )
    .join('\n\n')

  return [
    {
      role: 'system',
      content:
        `You are a PMP study advisor. Reply in ${replyLang}. ` +
        'Create a structured study plan with markdown headings: ' +
        '## Priority Areas, ## Recommended Focus, ## Study Tips, ## Next Steps. ' +
        'Be specific to the weak tasks and mistake patterns below.',
    },
    {
      role: 'user',
      content: truncate(
        `Task accuracy (weakest first):\n${statsBlock}\n\n` +
          `Sample wrong answers:\n${wrongBlock || '(none)'}`,
        3000,
      ),
    },
  ]
}

/** @type {import('@commitlint/types').UserConfig} */
export default {
  extends: ['@commitlint/config-conventional'],
  rules: {
    'type-enum': [
      2,
      'always',
      [
        'feat','fix','docs','style','refactor','perf','test',
        'build','ci','chore','revert','deprecate'
      ]
    ],
    'subject-case': [2, 'never', ['sentence-case','start-case','pascal-case','upper-case']],
    'footer-leading-blank': [1, 'always'],
    'body-leading-blank': [1, 'always'],
    'body-max-line-length': [0, 'always', 0]
  },
  prompt: {
    messages: {},
    questions: {}
  }
};

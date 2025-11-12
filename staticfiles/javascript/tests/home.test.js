/**
 * @jest-environment jsdom
 */
const { filterProjects } = require('../home'); // adjust path

describe('filterProjects', () => {
  beforeEach(() => {
    document.body.innerHTML = `
      <input id="name-search" value="app" />
      <div class="project" data-name="my app"></div>
      <div class="project" data-name="website"></div>
    `;
  });

  it('shows matches and hides non-matches', () => {
    const nameSearch = document.getElementById('name-search');
    const projects   = document.querySelectorAll('.project');

    filterProjects(nameSearch, projects);

    const [matchEl, nonMatchEl] = projects;
    expect(matchEl.style.display).toBe('');
    expect(nonMatchEl.style.display).toBe('none');
  });
});

import { KefaAppPage } from './app.po';

describe('kefa-app App', () => {
  let page: KefaAppPage;

  beforeEach(() => {
    page = new KefaAppPage();
  });

  it('should display welcome message', () => {
    page.navigateTo();
    expect(page.getParagraphText()).toEqual('Welcome to app!!');
  });
});

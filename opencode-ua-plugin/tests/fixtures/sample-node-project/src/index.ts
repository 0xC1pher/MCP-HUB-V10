export function greet(name: string): string { return `Hello, ${name}!`; }
export class UserService {
  async getUser(id: string) { return { id, name: "Test" }; }
}
